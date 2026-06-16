# 📅 日期
2026-05-20 ~ 2026-05-25

# 📁 类名 - 分支名
`HRCatLitterBoxActivity` — `feat_v3.5.5`

# ← 来源文档
`读懂-HRCatLitterBoxActivity [猫砂盆设置页] -P0-2026-05-20.md`

---

# 🧠 术语与概念速查

| 术语                  | 含义                                  | 接口方法                       | 示例                              |
|-----------------------|---------------------------------------|--------------------------------|-----------------------------------|
| 物模型 (ThingModel)   | 当前设备支持的全部属性/服务/事件定义   | `fetchProductsThingMode()`     | 100a+ 支持 `remote_refill` 服务   |
| 物模型属性 (Property) | 设备上报的实时数据（传感器数据）       | `fetchDeviceProperty()`        | `toilet_litter_status` 砂仓余量   |
| 物模型服务 (Service)  | 可下发的远程控制指令                   | `invokeDeviceService()`        | `remote_clean` 立即清理           |
| PK (productKey)       | 产品系列标识（一个系列共用）           | -                              | `A9015201` 代表某款猫砂盆系列     |
| 设备序列号 (sn)       | 具体某台设备的唯一标识                 | -                              | 用于查询单台设备的物模型           |

---

# 💀 实现1：添加补砂、开集便箱门、开口朝上按钮，物模型控制显隐 ActionItem

## 1. 需求描述
根据设备物模型，动态显示/隐藏快捷操作按钮（如补砂、开集便箱门、开口朝上），100a 和 100a+ 设备支持的按钮不同。

## 2. 我的疑问（不懂的地方）

> ❓ Q1: 100a 补砂按钮对应的物模型是 `remote_refill` 吗？那任务类型 `task_type` 里面的 `refilling` 加砂中是什么？
>
> ✅ A1: 加砂中是上报的一个补砂属性，设备在加砂的状态 ing。`remote_refill` 是下发指令，`refilling` 是上报状态，两个不一样。

> ❓ Q2: 100a 和 100a+ 的砂仓余量对应的物模型的标识符 identifier 是什么？
>
> ✅ A2: 是如厕桶，`toilet_litter_status`。

> ❓ Q3: 方法中的 `thingModel` 是全量物模型吗？是从哪个接口获取到全量物模型，源头是在哪里？
>
> ✅ A3: 是 `HRBaseDeviceActivity` 中的方法 `fetchProductsThingMode()` 获取的。

> ❓ Q4: `updateThingModelUI()` 在父类 `HRBaseActivity.oncreate()` 方法中的 `fetchProductsThingMode()` 就被调用了，所以是最新的。然后更新 `HRCatLitterBoxActivity.updateActionDisplayList()`？
>
> ✅ A4: 是的，`updateThingModelUI()` 在父类 `HRBaseActivity` 的 `oncreate()` 中的 `fetchProductsThingMode()` 被调用，加载完成后回调 `updateThingModelUI()`，然后更新 `updateActionDisplayList()`。所以是全量物模型在前面，物模型更新页面方法`updateThingModelUI()`和属性控制任务面板和余量数据方法`onPropertyUpdate()`都是在接口调用之后




## 3. 关键代码链路

```
HRBaseDeviceActivity.initView()
  └→ fetchProductsThingMode()
       ├→ 1. 查设备级 SP 缓存 (KEY_THING_MODEL_DATA_PREFIX + sn)
       ├→ 2. 查产品级 SP 缓存 (KEY_THING_MODEL_DATA_PREFIX + pk)
       ├→ 3. 读 Assets 全量文件 products_all_thing_models.json
       └→ 4. 调接口 fetchDeviceThingModel() 实时更新
            └→ API: GET /v1/devices/{sn}/thing_model?version={localVersion}
  └→ 加载完成后回调 updateThingModelUI()
       └→ 过滤 supportedModels（物模型里有这个服务才保留）
       └→ 构建 allActionItems 列表
       └→ 调用 updateActionDisplayList() 更新 UI
```

## 4. thingModel 物模型数据来源

### 4.1 获取单个设备的物模型（设备维度缓存 + 实时更新）

API: GET /v1/devices/{deviceName}/thing_model?version={localVersion}
返回的响应：
{
    "data": null,
    "version": "string"
}
data有时候是null,后端的逻辑是查看version是最新的就不会返回设备物模型

接口作用：设备物模型的故障事件更新等，

```java
// HmCommonNetUtils.fetchDeviceThingModel()
// API: GET /v1/devices/{deviceName}/thing_model?version={localVersion}
@JvmStatic
@JvmOverloads
fun fetchDeviceThingModel(
    lifecycleOwner: LifecycleOwner,
    deviceName: String,
    callback: HmNetworkCallback<HrProductsThingModel?>? = null,
    isHandlerError: Boolean = false,
) {
    val versionKey = SPConstant.KEY_THING_MODEL_VERSION_PREFIX + deviceName
    val dataKey = SPConstant.KEY_THING_MODEL_DATA_PREFIX + deviceName
    val localVersion = SPUtils.getInstance().getString(versionKey)

    lifecycleOwner.scopeNetLife {
        val res = Get<HMBaseResponse<HrProductsThingModel?>?>(HmApi.fetchDeviceThingModel(deviceName)) {
            setQuery("version", localVersion.orEmpty())
        }.await()

        val remoteVersion = res?.version
        val remoteData = res?.data

        // 如果后端返回了新数据，且版本不一致，则更新缓存
        if (remoteData != null && remoteVersion != localVersion) {
            if (!remoteVersion.isNullOrEmpty()) {
                SPUtils.getInstance().put(versionKey, remoteVersion)
            }
            val singleJson = Gson().toJson(remoteData)
            SPUtils.getInstance().put(dataKey, singleJson)
            callback?.onSuccess(remoteData)
        }
    }.catch {
        if (it is Exception) {
            callback?.onError(it)
        }
        if (isHandlerError) {
            handleError(it)
        }
    }
}
```

### 4.2 获取产品物模型定义（异步）
 
 val deviceCachedJson = SPUtils.getInstance().getString(deviceDataKey)
 Gson().fromJson(deviceCachedJson, HrProductsThingModel::class.java)

将之前存的全量物模型数据，通过Gson()序列化转变为List<HrProductsThingModel>


```java
// HRBaseDeviceActivity.fetchProductsThingMode()
protected fun fetchProductsThingMode() {
    val pk = productKey.lowercase()
    val sn = deviceSerial

    if (sn.isNotEmpty()) {
        val deviceDataKey = SPConstant.KEY_THING_MODEL_DATA_PREFIX + sn
        val deviceCachedJson = SPUtils.getInstance().getString(deviceDataKey)
        var hasDeviceCache = false

        // 先尝试查设备级缓存，如果查到就直接用
        if (!deviceCachedJson.isNullOrEmpty()) {
            try {
                val cachedModel = Gson().fromJson(deviceCachedJson, HrProductsThingModel::class.java)
                if (cachedModel != null) {
                    thingModel = cachedModel
                    updateThingModelUI()
                    hasDeviceCache = true
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }

        // 补充兜底逻辑：设备缓存不存在或加载失败，先用产品维度兜底占位
        if (!hasDeviceCache) {
            fetchProductThingModelFallback(pk)
        }

        // 无论是否有缓存，都同步去调用接口，去更新数据
        HmCommonNetUtils.fetchDeviceThingModel(this, sn, object : HmNetworkCallback<HrProductsThingModel?> {
            override fun onSuccess(result: HrProductsThingModel?) {
                if (result != null) {
                    thingModel = result
                    updateThingModelUI()
                }
            }
            override fun onError(error: Exception) {}
        })
    } else {
        // 没有序列号，直接走产品维度逻辑
        fetchProductThingModelFallback(pk)
    }
}

// 兜底逻辑：尝试从产品维度 SP 缓存或 Assets 核心库读取
private fun fetchProductThingModelFallback(pk: String) {
    lifecycleScope.launch(Dispatchers.IO) {
        val dataKey = SPConstant.KEY_THING_MODEL_DATA_PREFIX + pk
        val cachedJson = SPUtils.getInstance().getString(dataKey)

        // 1. 尝试从 SharedPreference 缓存读取 (产品维度)
        if (!cachedJson.isNullOrEmpty()) {
            try {
                val cachedModel = Gson().fromJson(cachedJson, HrProductsThingModel::class.java)
                if (cachedModel != null) {
                    launch(Dispatchers.Main) {
                        thingModel = cachedModel
                        updateThingModelUI()
                    }
                    return@launch
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }

        // 2. 尝试从 Assets 核心库读取全量文件
        try {
            assets.open("products_all_thing_models.json").bufferedReader().use { it.readText() }.let { assetsJson ->
                val type = object : TypeToken<HMBaseResponse<Map<String, HrProductsThingModel>>>() {}.type
                val fullResponse: HMBaseResponse<Map<String, HrProductsThingModel>>? = Gson().fromJson(assetsJson, type)
                val allModels = fullResponse?.data
                if (allModels != null) {
                    val model = allModels[pk]
                    if (model != null) {
                        launch(Dispatchers.Main) {
                            thingModel = model
                            updateThingModelUI()
                        }
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}

// 物模型加载成功后的解析回调（子类重写）
protected open fun updateThingModelUI() {}
```

## 5. 核心代码

```java
override fun updateThingModelUI() {
    super.updateThingModelUI()

    // 1. 余量监控区域显隐
    val hasLitterStatus = thingModel?.getProperty(DevicePropertyConstants.TOILET_LITTER_STATUS) != null
    val hasWasteStatus = thingModel?.getProperty(DevicePropertyConstants.WASTE_BIN_FULL_STATUS) != null
    val hasRefillStatus = thingModel?.getProperty(DevicePropertyConstants.REFILL_LITTER_STATUS) != null

    mBind.rlLitterAmount.visibleOrGone(hasLitterStatus)
    mBind.rlToiletBoxCapacity.visibleOrGone(hasWasteStatus)
    mBind.llMargin.visibleOrGone(hasLitterStatus || hasWasteStatus)

    // 2. 100a+ 新 UI 切换逻辑
    if (hasRefillStatus && hasWasteStatus && hasLitterStatus) {
        mBind.llNewUi.visibleOrGone(true)
        mBind.llMargin.visibleOrGone(false)
        mBind.rlSurplus1.visibleOrGone(hasRefillStatus && hasLitterStatus)
        mBind.rlSurplus2.visibleOrGone(hasWasteStatus)
    }

    // 3. 快捷操作按钮过滤（只保留物模型里有的服务）
    supportedModels = setOf(
        "remote_clean", "remote_level", "remote_empty",
        "remote_refill", "remote_lid", "remote_open_up"
    ).filter { thingModel.contains(it) }.toSet()

    val allActionItems = mutableListOf(
        ActionItem(getString(R.string.catlitterbox_btn_clean_now), R.mipmap.ic_quick_operation_clean_up, "remote_clean"),
        ActionItem(getString(R.string.catLitterBox_text_flatten), R.mipmap.ic_quick_operation_smooth_out, "remote_level"),
        ActionItem(getString(R.string.catlitterbox_text_sand_clearing_action), R.mipmap.ic_quick_operation_empty_the_cat_litter, "remote_empty"),
        ActionItem(getString(R.string.catLitterBox_text_refillCatLitter), R.mipmap.ic_quick_manual_san_replenishment, "remote_refill"),
        ActionItem(getString(R.string.catLitterBox_text_openToiletDoor), R.mipmap.ic_quick_open_toilet_collection_box_door, "remote_lid"),
        ActionItem(getString(R.string.catLitterBox_text_openUpwards), R.mipmap.ic_quick_open_upwards, "remote_open_up"),
    ).filter { it.identifier in supportedModels }.toMutableList()
}
```

## 6. 踩坑记录

> ⚠️ 坑点：xml 里的 `<include>` 标签有没有写 `android:id`，有 id 就加一层，直接用 `binding.closeBtn` 是用不了的
>
> 🔧 解决：必须写 id，有 id 就加一层。

---

# 💀 实现2：猫砂余量数据显示的逻辑

## 1. 需求描述
显示砂仓余量、补砂桶余量、集便箱余量的实时状态（充足/不足），点击可跳转余量详情页。

## 2. 我的疑问（不懂的地方）

> ❓ Q3: 余量 UI 的显示是要查看属性值的，所调用的接口是什么？
>
> ✅ A3: 调用的是 `HmCommonNetUtils` 中的 `fetchDeviceProperty()`，但不直接用，套一层用 `HRBaseDeviceActivity` 中的 `fetchDeviceProperty()`。

## 3. 关键代码链路

```
HRBaseDeviceActivity.fetchDeviceProperty(useCache)
  └→ HmCommonNetUtils.fetchDeviceProperty(lifecycleOwner, deviceName, callback, useCache)
       ├→ 1. 先读本地缓存 (CacheMode.READ)
       └→ 2. 再请求网络 (CacheMode.WRITE)
            └→ API: GET /v1/devices/{deviceName}/property
  └→ 回调 onPropertyUpdate(result: Map<String, Any?>)
       ├→ A. 传感器数据更新（余量状态文字/颜色）
       └→ B. 任务状态解析 handleDeviceTaskStatus(result)
```

## 4. 物模型属性 Property 来源

### 4.1 封装接口 HmCommonNetUtils 网络请求

API: GET /v1/devices/$device_name/properties
返回响应数据：
{
    "data": {
        "bed_heater_switch": false,
        "bed_target_temp": 25,
        "mode": 0,
        "switch": false,
        "target_temp": 21,
        "voice_level": 0,
        "voice_switch": true,
        "online_status": true
    }
}
物模型属性值


```java
// API: GET /v1/devices/$device_name/properties
@JvmStatic
@JvmOverloads
fun fetchDeviceProperty(
    lifecycleOwner: LifecycleOwner,
    deviceName: String,
    callback: HmNetworkCallback<Map<String, Any?>>,
    isHandlerError: Boolean = false,
    useCache: Boolean = true,
) {
    lifecycleOwner.scopeNetLife {
        // 网络请求（并写入缓存）
        val data = Get<Map<String, Any?>>(HmApi.getDeviceProperty(deviceName)) {
            setCacheKey("device_prop_$deviceName")
            setCacheMode(CacheMode.WRITE)
        }.await()
        callback.onSuccess(data)
    }.let { scope ->
        if (useCache) {
            scope.preview {
                // 先读取缓存
                val cachedData = Get<Map<String, Any?>>(HmApi.getDeviceProperty(deviceName)) {
                    setCacheKey("device_prop_$deviceName")
                    setCacheMode(CacheMode.READ)
                }.await()
                callback.onSuccess(cachedData)
            }.catch { }
        }
        scope
    }.catch {
        if (it is Exception) {
            callback.onError(it)
        }
        if (isHandlerError) {
            handleError(it)
        }
    }
}
```

### 4.2 HRBaseDeviceActivity 封装层

Kotlin 的命名参数允许跳过有默认值的参数。
    HmCommonNetUtils.fetchDeviceProperty()方法中的参数isHandlerError: Boolean = false有默认值false，所以可以跳过

```java
protected fun fetchDeviceProperty(useCache: Boolean = true) {
    val serial = deviceSerial.uppercase()
    HmCommonNetUtils.fetchDeviceProperty(
        this, serial,
        object : HmNetworkCallback<Map<String, Any?>> {
            override fun onSuccess(result: Map<String, Any?>) {
                // 统一提取实时在线状态
                if (result.containsKey(DevicePropertyConstants.ONLINE_STATUS)) {
                    status = if (result[DevicePropertyConstants.ONLINE_STATUS].toSafeBoolean()) 1 else 0
                }
                onPropertyUpdate(result)
            }
            override fun onError(error: Exception) {
                onPropertyError(error)
            }
        }, useCache = useCache
    )
}
```

## 5. 核心代码

### 5.1 余量 UI 显隐（物模型属性控制）

```java
override fun updateThingModelUI() {
    super.updateThingModelUI()

    val hasLitterStatus = thingModel?.getProperty(DevicePropertyConstants.TOILET_LITTER_STATUS) != null
    val hasWasteStatus = thingModel?.getProperty(DevicePropertyConstants.WASTE_BIN_FULL_STATUS) != null
    val hasRefillStatus = thingModel?.getProperty(DevicePropertyConstants.REFILL_LITTER_STATUS) != null

    mBind.rlLitterAmount.visibleOrGone(hasLitterStatus)
    mBind.rlToiletBoxCapacity.visibleOrGone(hasWasteStatus)
    mBind.llMargin.visibleOrGone(hasLitterStatus || hasWasteStatus)

    if (hasRefillStatus && hasWasteStatus && hasLitterStatus) {
        mBind.llNewUi.visibleOrGone(true)
        mBind.llMargin.visibleOrGone(false)
        mBind.rlSurplus1.visibleOrGone(hasRefillStatus && hasLitterStatus)
        mBind.rlSurplus2.visibleOrGone(hasWasteStatus)
    }

    updateFragmentStatus()
}
```

### 5.2 更新"充足"数据（物模型属性展示余量 UI）

```java
override fun onPropertyUpdate(result: Map<String, Any?>) {
    mBind.prlContent.finishRefresh()

    // A. 砂仓余量（100a/100a+ 共用）
    if (result.containsKey(DevicePropertyConstants.TOILET_LITTER_STATUS)) {
        val toiletRemainStatus = result[DevicePropertyConstants.TOILET_LITTER_STATUS].toSafeBoolean()
        mBind.tvLitterAmountValue.text =
            if (toiletRemainStatus) getString(R.string.catlitterbox_label_sufficient) else getString(R.string.catlitterbox_label_insufficient)
        mBind.tvLitterAmountValue.setTextColor(if (toiletRemainStatus) getCompatColor(R.color.color_383231) else getCompatColor(R.color.color_ff2742))

        // 100a+ 砂仓余量
        mBind.tvSandBinValue.text =
            if (toiletRemainStatus) getString(R.string.catlitterbox_label_sufficient) else getString(R.string.catlitterbox_label_insufficient)
        mBind.tvSandBinValue.setTextColor(if (toiletRemainStatus) getCompatColor(R.color.color_383231) else getCompatColor(R.color.color_ff2742))
    }

    // B. 补砂桶余量（100a+ 专属）
    if (result.containsKey(DevicePropertyConstants.REFILL_LITTER_STATUS)) {
        val refillRemainStatus = result[DevicePropertyConstants.REFILL_LITTER_STATUS].toSafeBoolean()
        mBind.tvSandReplenishmentBucketValue.text =
            if (refillRemainStatus) getString(R.string.catlitterbox_label_sufficient) else getString(R.string.catlitterbox_label_insufficient)
        mBind.tvSandReplenishmentBucketValue.setTextColor(if (refillRemainStatus) getCompatColor(R.color.color_383231) else getCompatColor(R.color.color_ff2742))
    }

    // C. 集便箱余量
    if (result.containsKey(DevicePropertyConstants.WASTE_BIN_FULL_STATUS)) {
        val wasteBinStatus = result[DevicePropertyConstants.WASTE_BIN_FULL_STATUS].toSafeBoolean()
        mBind.tvToiletBoxValue.text =
            if (wasteBinStatus) getString(R.string.common_text_notEnough) else getString(R.string.catLitterBox_text_normal)
        mBind.tvToiletBoxValue.setTextColor(if (wasteBinStatus) getCompatColor(R.color.color_ff2742) else getCompatColor(R.color.color_383231))

        // 100a+ 集便箱门
        mBind.tvToiletWasteTankValue.text =
            if (wasteBinStatus) getString(R.string.common_text_notEnough) else getString(R.string.catLitterBox_text_normal)
        mBind.tvToiletBoxValue.setTextColor(if (wasteBinStatus) getCompatColor(R.color.color_ff2742) else getCompatColor(R.color.color_383231))
    }
}
```

### 5.3 按钮跳转

```java

    listOf(mBind.rlSurplus1 to 0,mBind.rlSurplus2 to 1).forEach {(view, type) ->
        view.singleClick {
            val intent = Intent(this, DeviceCatLitterBoxSurplus3Activity::class.java)
            intent.putExtra("device_model", deviceModel)
            intent.putExtra("type", type)
            startActivity(intent)
        }  
    }
```

## 6. device_model 数据来源

```java
// 1. HRBaseDeviceActivity 从 Intent 中获取
protected open val deviceModel: DevicesModel.DataDTO.ListDTO? by lazy {
    intent.getSerializableExtra("device_model") as? DevicesModel.DataDTO.ListDTO
}

// 2. 从 HomeV2Fragment 获取设备列表
// API: POST /app/v1/devices/list
private fun getDeviceList() {
    val params: MutableMap<String, Any> = HashMap()
    params["familyId"] = familyId
    if (familyRoomId != 0) {
        params["familyRoomId"] = familyRoomId
    }
    params["page"] = page
    params["limit"] = limit
    val map = ApiClient.createParam(params)
    apiService.devicesList(map)
        .subscribeOn(Schedulers.io())
        .observeOn(AndroidSchedulers.mainThread())
        .subscribe(object : SingleObserver<DevicesModel> {
            override fun onSubscribe(d: Disposable) {}
            override fun onSuccess(model: DevicesModel) {
                if (model.code == "200") {
                    devicesList = model.data.list.toMutableList()
                    if (familyRoomId == 0) {
                        val str = Gson().toJson(devicesList)
                        SharedPreferencesUtils.setStringValue(StaticDataUtils.devicesList, str)
                    }
                    homeDeviceAdapter.setNewInstance(devicesList)
                    mBind.recyclerView.visibility = if (devicesList.size == 0) View.GONE else View.VISIBLE
                    mBind.noDeviceView.visibility = if (devicesList.size == 0) View.VISIBLE else View.GONE
                }
            }
            override fun onError(e: Throwable) {}
        })
}
```

---

# 🏁 踩坑记录汇总

| 日期  | 坑点                                   | 原因                   | 解决方案                                    |
|-------|------------------------------------------|------------------------|---------------------------------------------|
| 5.20  | `<include>` 标签 binding 用不了           | 没写 `android:id`       | 必须写 id，有 id 就加一层                    |
| 5.25  | 100a/100a+ 余量物模型标识符不同           | 迁移的是 100a+ 物模型   | 用 `refill_litter_status`，废弃旧版          |
| 5.25  | 余量页面跳转后 `device_model` 为空        | 忘记 Intent 传参        | `intent.putExtra("device_model", deviceModel)` |

---

# 💀 实现3：属性轮询与设备特征识别

## 1. 需求描述
根据设备序列号动态获取设备属性值列表，识别设备硬件特征（如是否有摄像头），并将属性数据分发到各个 UI 模块进行状态更新。

## 2. 关键代码链路

```
属性轮询 (HRBaseDeviceActivity.startPropertyPolling)
  └→ HRBaseDeviceActivity.fetchDeviceProperty(useCache)
       └→ HmCommonNetUtils.fetchDeviceProperty(lifecycleOwner, deviceName, callback, isHandlerError, useCache)
            ├→ 1. 先读缓存 (CacheMode.READ)
            └→ 2. 再请求网络 (CacheMode.WRITE)
                 └→ API: GET /v1/devices/{deviceName}/properties
  └→ 回调 onPropertyUpdate(result: Map<String, Any?>)
       ├→ A. 传感器数据更新（余量状态文字/颜色）→ 见实现2
       ├→ B. 任务状态解析 handleDeviceTaskStatus(result) → 见实现4
       ├→ C. 基础设置状态同步（自动清理/幼猫保护/掩埋/风扇）
       ├→ D. 摄像头配套属性同步（补光灯/摄像头/麦克风）
       └→ E. 离线遮罩 + Fragment 状态同步
```

## 3. 轮询机制详解（HRBaseDeviceActivity）

### 3.1 轮询启动

```java
// HRCatLitterBoxActivity.initView() 末尾启动
startPropertyPolling()   // 属性轮询，间隔 2s
startEventPolling()      // 事件轮询，间隔 5s
```

### 3.2 轮询实现

```java

private var pollingPropertyJob: Job? = null
private var pollingEventJob: Job? = null


// HRBaseDeviceActivity — 属性轮询
protected fun startPropertyPolling(intervalMs: Long = 2000L) {
    pollingPropertyJob?.cancel()
    pollingPropertyJob = lifecycleScope.launch {
        repeatOnLifecycle(Lifecycle.State.RESUMED) {
            while (isActive) {
                fetchDeviceProperty(useCache = false)
                delay(intervalMs)
            }
        }
    }
}

// HRBaseDeviceActivity — 事件轮询
protected fun startEventPolling(intervalMs: Long = 5000L) {
    pollingEventJob?.cancel()
    pollingEventJob = lifecycleScope.launch {
        repeatOnLifecycle(Lifecycle.State.RESUMED) {
            while (isActive) {
                fetchDeviceEvents()
                delay(intervalMs)
            }
        }
    }
}
```

### 3.3 协程与 Job 机制梳理

轮询的本质：在 `lifecycleScope`（SupervisorJob）里启动协程，`repeatOnLifecycle` 跟随 Activity 生命周期，`while + delay` 实现循环。

**层级拆解：**

```
lifecycleScope (SupervisorJob 协程域，与 Activity 生命周期绑定)
  └→ launch {} → 返回 Job (pollingPropertyJob)
       └→ repeatOnLifecycle(RESUMED) → 监听 Activity 生命周期
            └→ while(isActive) { fetch(); delay() } → 循环体
```

三层各司其职：
- `lifecycleScope` + SupervisorJob = 协程域，一个子协程崩了不影响其他兄弟协程
- `repeatOnLifecycle(RESUMED)` = Activity 生命周期保护（切后台停，回来继续）
- `while + delay` = 循环（轮询）
- 三个组合 = 安全的轮询

**关键对象说明：**

`isActive` 不是变量，是协程内部属性，通过 `kotlin.coroutines.isActive` import

| 对象 | 类型 | 作用 |
|------|------|------|
| `lifecycleScope` | CoroutineScope (SupervisorJob) | Activity 协程域，DESTROYED 时取消所有子协程；子协程互不干扰 |
| `launch {}` | 返回 Job | 启动一个新协程，Job 可用于 cancel() 取消 |
| `pollingPropertyJob` | Job? | 协程的句柄，用于手动停止轮询 |
| `repeatOnLifecycle(RESUMED)` | 挂起函数 | 监听 Activity 生命周期，RESUMED 时启动，离开时取消，回来时重建 |
| `isActive` | 协程内部属性 | 协程未被取消时为 true，cancel() 后变 false 退出循环 |
| `delay(2000)` | 挂起函数 | 非阻塞等待 2s，期间协程挂起，不占线程 |

**轮询的完整生命周期：**

```
Activity.onCreate()
  └→ Activity 可见 → RESUMED
       └→ repeatOnLifecycle 启动循环 → while(isActive) { fetch → delay → fetch → ... }
            │
            ├→ 用户切后台 → STOPPED → repeatOnLifecycle 自动取消循环
            ├→ 用户回来 → RESUMED → repeatOnLifecycle 重新启动循环
            ├→ 调用 stopPropertyPolling() → pollingPropertyJob.cancel() → isActive=false → 退出循环
            └→ Activity.onDestroy() → lifecycleScope 取消所有协程 → 自动退出
```

**为什么先 cancel 再 launch？**

```kotlin
pollingPropertyJob?.cancel()  // 防止重复启动
pollingPropertyJob = lifecycleScope.launch { ... }
```

防止 `startPropertyPolling()` 被多次调用时产生多个轮询协程同时跑。

### 3.4 HRBaseDeviceActivity.onCreate() 初始化vs轮询顺序先后

```java
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    fetchMemberType(familyId)        // 1. 获取成员权限
    fetchProductsThingMode()          // 2. 加载物模型 → updateThingModelUI()
    fetchDeviceProperty(useCache = false)  // 3. 首次拉取属性（不等轮询）
}
// initView() 由子类实现，轮询在子类 initView() 末尾启动

所以轮询调用顺序是在子类，比接口晚

```

### 3.5 防回跳保护与轮询的配合

`onPropertyUpdate()` 中通过 `isActionProtecting()` 判断是否跳过 `handleDeviceTaskStatus()`，避免轮询旧数据覆盖 Mock 状态。详见 **实现4 第8节 防回跳保护机制**。

## 4. 设备特征识别自研设备进入才能进入到该页面（ProductUtils）

通过设备序列号（productKey）查询产品信息，判断设备硬件特征：

```java
// initView() 中获取产品信息
val product = withContext(Dispatchers.IO) {
    ProductUtils.getProductByDeviceSerial(productKey)
}
hasCamera = product?.is_ipc == true
```

```java
// ProductUtils：PK 是产品系列标识，SN 是具体设备标识
object ProductUtils {
    const val MODEL_CAT_LITTER_BOX_A1 = "A9015201"  // 75v
    const val MODEL_CAT_LITTER_BOX_A2 = "A9015202"
    const val MODEL_CAT_LITTER_BOX_B1 = "B9015201"  // 100a
    const val MODEL_CAT_LITTER_BOX_B2 = "B9015202"  // 100a+

    fun isSelfDevelopedCatLitterBox(model: String?): Boolean {
        val m = model?.uppercase(Locale.getDefault())
        return m == MODEL_CAT_LITTER_BOX_A1 || m == MODEL_CAT_LITTER_BOX_A2 ||
               m == MODEL_CAT_LITTER_BOX_B1 || m == MODEL_CAT_LITTER_BOX_B2
    }

        /**
     * 根据设备序列号获取产品信息
     */
    fun getProductByDeviceSerial(deviceSerial: String?): Product? {
        val processedSerialKey = deviceSerial
            ?.substringBefore(":")
            ?.uppercase(Locale.getDefault())
            .orEmpty()

        val spJson = SPUtils.getInstance().getString(SPConstant.KEY_GET_PRODUCT_JSON, "")
        return spJson.takeIf { !it.isNullOrEmpty() }
            ?.let {
                runCatching {
                    GsonUtils.fromJson<List<CategoryProductData?>?>(
                        it,
                        object : TypeToken<List<CategoryProductData?>?>() {}.type
                    )
                }.getOrNull()
            }
            ?.let { flattenCategoryProducts(it) }
            ?.find { product ->
                product.product_keys?.any { key ->
                    key.equals(processedSerialKey, ignoreCase = true)
                } == true
            }
    }
}
```

## 5. onPropertyUpdate() 分发总览

轮询拿到属性数据后，`onPropertyUpdate()` 是中枢分发站，具体代码在各实现里：

| 分段 | 处理内容 | 受防回跳保护 | 详细代码位置 |
|------|----------|-------------|-------------|
| A | 余量传感器数据（砂仓/补砂桶/集便箱） | 否 | 实现2 第5.2节 |
| B1 | 任务状态 `handleDeviceTaskStatus()` | **是** | 实现4 第5节 + 第8节 |
| B2 | 基础设置（自动清理/幼猫保护/掩埋/风扇） | **是** | 同步到 Fragment 状态卡片 |
| C | 摄像头属性（补光灯/摄像头开关/麦克风/摄像头状态） | 否 | 同步到直播 Fragment |
| D | 离线遮罩 | 否 | 一行判断 |

防回跳保护的完整判断逻辑见 **实现4 第8.4节**。


---

# 💀 实现4：任务状态 UI 控制（底部操作栏 + 标题栏）

## 1. 需求描述
根据设备上报的 `current_task.task_type` 和 `current_task.task_status`，控制底部操作栏和任务执行面板的显隐，以及标题栏状态文案的显示。

## 2. 核心概念：上报 vs 下发

| 方向 | 含义 | 涉及的物模型 | 代码入口 |
|------|------|-------------|----------|
| 上报 | 设备上报状态到云端，我们轮询查询 | `current_task`（含 `task_type` + `task_status`） | `fetchDeviceProperty()` → `onPropertyUpdate()` → `handleDeviceTaskStatus()` |
| 下发 | 我们向设备发送控制指令 | `remote_control_task`（含 `action`） | `handleActionClick()` → `invokeCatLitterService()` → `invokeDeviceService()` |

## 3. DeviceTaskType 与 DeviceTaskStatus 枚举

```java
enum class DeviceTaskType(val code: String) {
    IDLE("idle"),           // 空闲
    CLEANING("cleaning"),   // 自动清理/铲屎中
    REFILLING("refilling"), // 补砂中 (100a+)
    EMPTYING("emptying"),   // 清砂/一键排空猫砂
    SMOOTHING("leveling"),  // 平整猫砂/抚平
    MAINTAINING("maintaining"), // 维护模式（开口朝上）
    RESETTING("resetting"); // 设备复位/校准中
}

enum class DeviceTaskStatus(val code: Int) {
    IDLE(0),       // 待机/就绪
    RUNNING(1),    // 正在执行
    PAUSED(2),     // 已暂停
    COMPLETED(3),  // 已完成
    FAILED(4),     // 异常失败
    CANCELLED(5);  // 手动取消
}
```

## 4. task_type 75v和100a+设备相同物模型不同索引的映射机制

设备上报的 `task_type` 是数字索引（如 75v 、100a+的相同物模型不同索引），所以需要根据物模型 `specs.enum` 翻译为标准 Code：

```java
private fun getTaskTypeCodeFromSpecs(rawCode: Any?): String {
    // 1. 解析为整型索引
    val index = when (rawCode) {
        is Number -> rawCode.toInt()
        is String -> rawCode.toIntOrNull()
        else -> null
    }
    // 2. 优先从物模型 specs.enum 翻译
    if (index != null) {
        val enumList = thingModel?.getProperty(DevicePropertyConstants.TASK_TYPE)?.specs?.enum
        if (enumList != null && index >= 0 && index < enumList.size) {
            return enumList[index]
        }
        // 兜底硬编码映射
        return when (index) {
            0 -> "idle"; 
            1 -> "cleaning"; 
            2 -> "refilling"
            3 -> "emptying"; 
            4 -> "leveling"; 
            5 -> "maintaining"
            6 -> "resetting"; 
            else -> "idle"
        }
    }
    // 3. Mock 传入的字符串（如 "cleaning"）直接返回
    return (rawCode as? String) ?: "idle"
}
```

## 5. handleDeviceTaskStatus() — 任务面板 UI 控制

核心逻辑：根据 `taskType` + `taskStatus` 的组合决定底部显示哪个面板。

### 5.1 面板切换规则

```
活跃任务（显示 sllCurrentTask，隐藏 llBottomControl）：
  ├→ CLEANING/EMPTYING/SMOOTHING/RESETTING/REFILLING 且 RUNNING/PAUSED
  └→ MAINTAINING 且 IDLE（已完成开口朝上，需显示复位按钮）

空闲状态（显示 llBottomControl，隐藏 sllCurrentTask）：
  └→ 其余所有情况
```

### 5.2 开口朝上的三步状态流转

```
步骤1: 开口朝上运行中 (MAINTAINING + RUNNING)
  → 取消按钮变"复位"，灰色不可点
  → 暂停/继续按钮正常

步骤2: 已完成开口朝上 (MAINTAINING + IDLE)
  → 复位按钮可点
  → 暂停/继续按钮隐藏
  → 中间文字："已完成开口朝上"

步骤3: 开口复位中 (RESETTING + RUNNING)
  → 复位按钮隐藏
  → 暂停/继续按钮正常显示
```

### 5.3 完整代码

```java
private fun handleDeviceTaskStatus(result: Map<String, Any?>) {
    val currentTaskObj = result[DevicePropertyConstants.CURRENT_TASK]
    var taskTypeCode = "idle"
    var taskStatusCode = 0

    if (currentTaskObj is Map<*, *>) {
        val rawTaskType = currentTaskObj[DevicePropertyConstants.TASK_TYPE]
        taskTypeCode = getTaskTypeCodeFromSpecs(rawTaskType)
        taskStatusCode = (currentTaskObj[DevicePropertyConstants.TASK_STATUS] as? Number)?.toInt() ?: 0
    }

    this.taskType = DeviceTaskType.fromCode(taskTypeCode)
    this.taskStatus = DeviceTaskStatus.fromCode(taskStatusCode)
    this.isCatInside = (result[DevicePropertyConstants.CAT_INSIDE] as? Boolean) == true
    this.isCatNear = (result[DevicePropertyConstants.CAT_NEARBY] as? Boolean) == true

    // 判断是否显示任务面板
    val showTaskPanel = (
        (taskType in listOf(CLEANING, EMPTYING, SMOOTHING, RESETTING, REFILLING, MAINTAINING) &&
         taskStatus in listOf(RUNNING, PAUSED))
        || (taskType == MAINTAINING && taskStatus == IDLE)  // 已完成开口朝上
    )

    if (showTaskPanel) {
        mBind.llBottomControl.visibility = View.GONE
        mBind.sllCurrentTask.visibility = View.VISIBLE

        // 默认状态：取消可点，暂停/继续可点
        mBind.llCancel.visibility = View.VISIBLE
        mBind.llContinuePause.visibility = View.VISIBLE
        mBind.llCancel.alpha = 1.0f; mBind.llCancel.isEnabled = true
        mBind.llContinuePause.alpha = 1.0f; mBind.llContinuePause.isEnabled = true
        mBind.tvCancelDesc.text = getString(R.string.catlitterbox_button_cancel)

        // 特殊状态覆盖
        when {
            taskType == MAINTAINING && taskStatus == IDLE -> {
                // 步骤2：已完成开口朝上
                mBind.llContinuePause.visibility = View.GONE
                mBind.tvCancelDesc.text = getString(R.string.catlitterbox_text_reset)
                mBind.ivCancelIcon.setImageResource(R.mipmap.ic_open_up_reset)
                mBind.tvEventDesc.text = getString(R.string.catlitterbox_text_status_open_up_completed)
            }
            taskType == RESETTING -> {
                // 步骤3：复位中
                mBind.llCancel.visibility = View.GONE
            }
            taskType == MAINTAINING -> {
                // 步骤1：开口朝上运行/暂停中
                mBind.tvCancelDesc.text = getString(R.string.catlitterbox_text_reset)
                mBind.llCancel.alpha = 0.5f; mBind.llCancel.isEnabled = false
            }
        }

        // 猫咪靠近/进入 → 全部置灰
        if (isCatInside || isCatNear) {
            mBind.tvEventDesc.text = if (isCatInside) "猫咪在仓内，已暂停" else "猫咪靠近，已暂停"
            mBind.llCancel.alpha = 0.5f; mBind.llCancel.isEnabled = false
            mBind.llContinuePause.alpha = 0.5f; mBind.llContinuePause.isEnabled = false
            mBind.tvPauseContinue.text = "继续"
            mBind.ivPauseContinue.setImageResource(R.mipmap.ic_equipment_continue)
        } else if (taskStatus == PAUSED) {
            mBind.tvEventDesc.text = "设备暂停中"
            mBind.tvPauseContinue.text = "继续"
            mBind.ivPauseContinue.setImageResource(R.mipmap.ic_equipment_continue)
        } else {
            // 运行中：根据任务类型显示文案
            mBind.tvEventDesc.text = when (taskType) {
                RESETTING -> "复位中"; CLEANING -> "清理中"
                EMPTYING -> "清砂中"; REFILLING -> "补砂中"
                MAINTAINING -> "开口朝上中"; else -> "抚平中"
            }
            mBind.tvPauseContinue.text = "暂停"
            mBind.ivPauseContinue.setImageResource(R.mipmap.ic_equipment_on)
        }

        // 左侧图标
        mBind.ivEventIcon.setImageResource(when (taskType) {
            RESETTING -> R.mipmap.ic_quick_operation_reset
            CLEANING -> R.mipmap.ic_quick_operation_clean_up
            EMPTYING -> R.mipmap.ic_quick_operation_empty_the_cat_litter
            REFILLING -> R.mipmap.ic_quick_manual_san_replenishment
            MAINTAINING -> R.mipmap.ic_quick_open_upwards
            else -> R.mipmap.ic_quick_operation_smooth_out
        })
    } else {
        // 空闲：显示底部操作栏
        mBind.llBottomControl.visibility = View.VISIBLE
        mBind.sllCurrentTask.visibility = View.GONE
    }
    updateTitleStatus()
}
```

## 6. updateTitleStatus() — 标题栏状态

```
优先级：离线 > 有任务（暂停 > 运行）> 无任务（如厕中 > 在线）

离线        → "离线"
有任务暂停  → "设备暂停中"
有任务运行  → 根据任务类型显示（清理中/清砂中/抚平中/维护中/补砂中/复位中）
猫在仓内    → "猫咪如厕中"
空闲在线    → "在线"
```

## 7. 操作下发流程

### 7.1 快捷操作（handleActionClick → invokeCatLitterService）

点击按钮 → 弹确认框 → 调用 `invokeCatLitterService()` → 下发服务 → 成功后 Mock 状态立即更新 UI：

```java
// 下发服务接口
// API: POST /v1/devices/{deviceName}/service/{identifier}
// 请求体: { "data": { ...params } }
// 返回: { "result": 0 }  // 0 表示成功

private fun invokeCatLitterService(
    serviceId: String,              // 服务标识
    params: Map<String, Any?> = mapOf(),
    actionName: String? = null,     // Toast 提示名
    mockTaskType: String? = null,   // 成功后模拟的 task_type
    mockTaskStatus: Int? = null     // 成功后模拟的 task_status
) {
    invokeDeviceService(serviceId, params, object : HmNetworkCallback<Any?> {
        override fun onSuccess(result: Any?) {
            if (result is Map<*, *>) {
                val resultCode = (result["result"] as? Number)?.toInt() ?: -1
                if (resultCode == 0) {
                    markActionTime()  // 防回跳保护
                    actionName?.let { Toaster.show("已下发${it}指令") }
                    if (mockTaskType != null && mockTaskStatus != null) {
                        handleDeviceTaskStatus(mapOf(
                            DevicePropertyConstants.CURRENT_TASK to mapOf(
                                DevicePropertyConstants.TASK_TYPE to mockTaskType,
                                DevicePropertyConstants.TASK_STATUS to mockTaskStatus
                            )
                        ))
                    }
                } else {
                    Toaster.show(CatLitterBoxTaskResult.getMsg(resultCode))
                }
            }
        }
        override fun onError(error: Exception) {}
    })
}
```

### 7.2 任务控制（invokeCatLitterBoxService）

任务面板上的"暂停/继续/取消/复位"按钮，统一走 `remote_control_task` 服务：

```java
private fun invokeCatLitterBoxService(action: Int) {
    val mockStatus = when (action) {
        0 -> DeviceTaskStatus.PAUSED.code    // 暂停
        1 -> DeviceTaskStatus.RUNNING.code   // 继续
        2 -> DeviceTaskStatus.RUNNING.code   // 取消 → 复位运行中
        3 -> DeviceTaskStatus.RUNNING.code   // 开口复位 → 复位运行中
        else -> DeviceTaskStatus.IDLE.code
    }
    val mockType = when (action) {
        2, 3 -> DeviceTaskType.RESETTING.code  // 取消/复位 → 任务类型变复位
        else -> taskType.code
    }
    invokeCatLitterService(
        serviceId = "remote_control_task",
        params = mapOf("action" to action),
        mockTaskType = mockType,
        mockTaskStatus = mockStatus
    )
}
```

### 7.3 action 值映射

| action | 含义 | 调用场景 |
|--------|------|----------|
| 0 | 暂停 | 任务运行中点击"暂停" |
| 1 | 继续 | 任务暂停中点击"继续" |
| 2 | 取消 | 非 MAINTAINING 任务点击"取消" |
| 3 | 开口复位 | MAINTAINING 完成后点击"复位" |

## 8. 防回跳保护机制

### 8.1 完整数据链路（轮询 × 下发 的交叉点）

防回跳是轮询（实现3）和下发服务（实现4）的交叉逻辑。下发改变状态，轮询读取状态，两者时序不一致就会出问题。

```
┌─ 下发链路（实现4）────────────────────────────────────────────┐
│  用户点击"清理"                                                │
│    → invokeCatLitterService("remote_clean")                    │
│      → invokeDeviceService() → API 下发                        │
│        → 成功(result=0)                                        │
│          → markActionTime()  ← 启动保护                        │
│          → handleDeviceTaskStatus(Mock数据) ← 立即更新UI        │
└───────────────────────────────────────────────────────────────┘

┌─ 轮询链路（实现3）────────────────────────────────────────────┐
│  startPropertyPolling() → 每2s循环                              │
│    → fetchDeviceProperty(useCache=false)                        │
│      → HmCommonNetUtils.fetchDeviceProperty()                  │
│        → API: GET /v1/devices/{sn}/properties                  │
│          → onSuccess(result) → onPropertyUpdate(result)        │
│            → if (isActionProtecting()) {  ← 检查保护           │
│                updateTitleStatus()  // 只更新在线状态            │
│                // 跳过 handleDeviceTaskStatus()                 │
│              } else {                                           │
│                handleDeviceTaskStatus(result) // 正常同步        │
│              }                                                  │
└───────────────────────────────────────────────────────────────┘
```

### 8.2 问题场景

```
t=0s  下发"清理"成功 → Mock CLEANING+RUNNING → UI显示"清理中" ✅
t=1s  轮询返回旧数据 IDLE → 不加保护的话 UI 闪回"在线" ❌ （回跳！）
t=3s  轮询返回新数据 CLEANING → UI 恢复"清理中" ✅
      原因：下发→设备执行→上报新状态 整条链路需要几秒，轮询不等人
```

### 8.3 保护代码（HRBaseDeviceActivity）

```java
// 保护时间戳
protected var lastActionTime: Long = 0L

// 下发成功时调用 → 启动保护
fun markActionTime() {
    lastActionTime = System.currentTimeMillis()
}

// 轮询回调时检查 → 是否在保护期
protected fun isActionProtecting(durationMs: Long = 5000L): Boolean {
    return System.currentTimeMillis() - lastActionTime < durationMs
}
```

### 8.4 onPropertyUpdate 中的保护判断

```java
override fun onPropertyUpdate(result: Map<String, Any?>) {
    // A. 传感器数据（余量）→ 不受保护影响，始终更新
    // ...

    // B. 任务状态 → 受保护控制
    if (isActionProtecting()) {
        // 保护期内：只更新在线状态，跳过任务面板
        updateTitleStatus()
    } else {
        // 保护期外：正常同步
        handleDeviceTaskStatus(result)
        // 同步基础设置...
    }

    // C. 摄像头属性 → 不受保护影响，始终更新
    // ...
}
```

### 8.5 触发 markActionTime() 的所有位置

| 调用位置 | 触发时机 |
|----------|----------|
| `invokeCatLitterService()` | 下发服务成功后 (result=0) |
| `updateDeviceProperty()` | 下发属性指令前 (通过父类封装) |

### 8.6 保护期结束后的自然恢复

5s 保护期结束后，设备已真正执行并上报了新状态，轮询拿到的就是最新数据，`handleDeviceTaskStatus()` 正常同步，UI 无缝衔接。

## 9. 踩坑记录

| 日期 | 坑点 | 原因 | 解决方案 |
|------|------|------|----------|
| 5.26 | 补砂时 title 不更新 | 下发成功后 Mock 状态，但轮询太快返回旧数据覆盖 | 防回跳保护 `isActionProtecting()` 跳过旧数据 |
| 5.26 | 75v 上报 task_type 是数字（如 6），不是字符串 | 不同设备物模型规格不同 | `getTaskTypeCodeFromSpecs()` 优先从物模型 specs.enum 翻译，兜底硬编码 |
| 5.26 | 虚拟设备 device_model 为空 | 虚拟设备上报属性只有 3 个字段，接口返回不完整 | 确认是虚拟设备限制，真机无此问题 |
