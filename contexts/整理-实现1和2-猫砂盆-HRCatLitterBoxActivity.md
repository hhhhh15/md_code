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
