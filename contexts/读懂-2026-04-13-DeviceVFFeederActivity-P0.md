# 📅 日期

2026-04-13

# 🏷️ 优先级
- [x] P0 — 马上要用到，必须搞懂
- [ ] P1 — 近期会用到
- [ ] P2 — 了解就好
- [ ] P3 — 先记录，以后再看

# 📁 类名 — 分支名

`DeviceVFFeederActivity` — `feat_v3.5.5`

# 🎯 本次阅读目标

> 这个页面是喂食器主页（带摄像头视频流），包含实时视频、设备动态、手动喂食、云存储等核心交互功能，搞清楚数据从哪来、怎么流转、最终展示到哪里。

---

# 积累的知识点

## 知识点1：item 布局写在适配器里，有两种方式：

  方式1：构造函数传入（BRVAH常见写法）
  // 构造时直接告诉适配器用哪个 item 布局
  weekListAdapter = new WeekListAdapter(R.layout.item_week_list_view, weekModelList);
  //                                    ↑ 这里就是 item 的 xml 文件

  方式2：适配器内部自己定义
  // CalendarAdapter 没有传布局ID
  CalendarAdapter adapter = new CalendarAdapter();
  // item 布局写在 CalendarAdapter.java 里面的 onCreateViewHolder() 方法里

## 知识点2：视频封面=视频首帧的提取和使用原理

  视频本质确实是连续帧的集合，比如 30fps 的视频每秒有 30
  张图片。但这些帧不是一个个独立的图片文件，而是被压缩编码（H.264/H.265）打包成一个视频文件存在 SD 卡上。

  所以流程是：

  SD卡上的视频文件（.mp4，H.264压缩）
    → 萤石SDK 解码视频流
    → 取出第一帧的原始像素数据
    → 以 byte[] 形式回调给你
    → BitmapFactory.decodeByteArray() 转成 Bitmap

  Glide 不能直接用的原因也在这：SD 卡上的视频没有 HTTP URL，而且即使有 URL，Glide
  也只能加载图片，不会去解码视频文件里的帧。

  所以你的理解是对的——视频就是帧的集合，可以从中取出某一帧，只是取帧这件事需要视频解码能力，萤石 SDK
  封装了这个能力，帮你做了解码，最后给你一个 byte[]。

**问题**
解码要怎么解码？
这个byte[]存的是什么数据形式，代表了什么数据含义？
Bitmap的数据形式是什么？


# 分析页面代码

| 行范围        | 内容                                                                                      |
|---------------|-------------------------------------------------------------------------------------------|
| 1 ~ 180       | imports                                                                                   |
| 181 ~ 406     | 类声明 + 所有成员变量（状态变量、云存储状态、视频列表、宠物列表等）                       |
| 408 ~ 444     | `onCreate()` — 初始化 RecordCoverFetcherManager                                           |
| 446 ~ 503     | 生命周期：`onStart` / `onStop` / `onDestroy` / `onPause` / `onResume`                     |
| 505 ~ 757     | `initUI()` — 所有 UI 组件绑定、ViewPager、Switch、RecyclerView 适配器、图表初始化         |
| 758 ~ 787     | `initTextSwitcher()` — 异常消息滚动展示初始化                                             |
| 775 ~ 787     | `setTextSwitcherView()` — 展示指定位置的异常消息，控制更多/关闭按钮显隐                   |
| 789 ~ 813     | `refreshView()` — 下拉刷新逻辑                                                            |
| 815 ~ 856     | `initDataView()` — 初始化数据视图（动态列表、云存状态）                                   |
| 858 ~ 881     | `initApi()` — 并发触发所有初始化 API 调用（8个）                                          |
| 883 ~ 1043    | `itemClick()` — 动态列表、事件类型列表的所有点击事件                                      |
| 1045 ~ 1073   | `loadVisibleItemCovers()` — 加载可见项封面（云存/本地双路分支）                           |
| 1075 ~ 1099   | `requestLocalCover()` — 本地封面请求（RecordCoverFetcherManager + BitmapCacheUtil）       |
| 1100 ~ 1115   | `getActionList()` / `getActionTypeList()` — 构建事件类型筛选列表                          |
| 1116 ~ 1128   | `changeView()` — 切换智能模式/电池模式 UI                                                 |
| 1130 ~ 1262   | `showCatLitterBoxAddPetDialog()` / `showCatLitterBoxPetRelationDialog()` — 宠物关联弹窗   |
| 1264 ~ 1283   | `setRecyclerViewHeightBasedOnItems()` — 动态计算 RecyclerView 高度                        |
| 1285 ~ 1295   | `onBackPressed()` — 返回键处理                                                            |
| 1296 ~ 1504   | `@OnClick` 注册 + `click()` — 所有点击事件分发                                            |
| 1506 ~ 1557   | `showCloudStoragePackage()` — 7天免费套餐弹窗                                             |
| 1559 ~ 1598   | `changeChartView()` — 切换折线图样式                                                      |
| 1601 ~ 1717   | `initChart()` — 折线图初始化（MPAndroidChart）                                            |
| 1719 ~ 1797   | `showCalendarDialog()` — 日期选择弹窗                                                     |
| 1799 ~ 1837   | `setupIndicators()` / `updateIndicators()` — 轮播指示器                                   |
| 1839 ~ 1858   | `updateBaterView()` — 更新电池图标样式                                                    |
| 1860 ~ 1892   | `showFeederNumDialog()` — 手动喂食份数选择弹窗（RulerView 1-20份）                        |
| 1893 ~ 2212   | 视频封面加载：`getCloudPicCoverImage1()` / `getCloudPicCoverImage()` / `getPicCoverImage1()` / `requestRecordCovers()` / `getPicCoverImage()` |
| 2213 ~ 2275   | `onGetMessage()` — EventBus Socket 事件（部分有实际处理逻辑）                             |
| 2276 ~ 2288   | `updateData()` — EventBus 数据更新事件                                                    |
| 2289 ~ 2570   | 物模型 Get/Set 方法（GetMachineTask、GetBaterIn、GetPowerMode、GetBatteryPercentage、SetManualFeed、GetCancelNextMeal、SetCancelNextMeal、GetLackFood、GetDesiccant、GetMealPlan、GetMicCtrl、SetMicCtrl、SetRemoteReboot、SetGeneralCmd3 等） |
| 2571 ~ 2852   | `devicesControl()` — 物模型透传核心方法（GET/PUT 统一处理，按 propIdentifier 分发结果更新 UI） |
| 2853 ~ 2936   | `devicesDynamicList()` — 设备动态列表，含封面加载触发                                     |
| 2937 ~ 2969   | `devicesExceptionStatusList()` — 设备异常列表                                             |
| 2970 ~ 3037   | `devicesStatus()` — 设备在线状态，触发 getMemberType() + initApi()                        |
| 3038 ~ 3069   | `devicesInfo()` — 获取设备详情                                                            |
| 3070 ~ 3103   | `getMemberType()` — 权限判断                                                              |
| 3104 ~ 3146   | `getPetInfoList()` — 宠物列表                                                             |
| 3147 ~ 3178   | `devicesDynamicPetList()` — 动态关联宠物                                                  |
| 3179 ~ 3233   | `getDevicesConfig()` / `setDevicesConfig()` — 单宠开关设置                                |
| 3234 ~ 3312   | `getProductFree()` — 待领取赠送套餐                                                       |
| 3313 ~ 3368   | `getOpenStatus()` — 云存开通状态，驱动视频列表或免费套餐分支                              |
| 3369 ~ 3451   | `getDevicesCloudStorageBanner()` — 云存 Banner（精彩时刻、看咪吃播）                      |
| 3452 ~ 3469   | `buildStorageIdMap()` — 构建 storageId → position 映射表                                  |
| 3470 ~ 3515   | `getStorageDownloadUrl()` — 获取云存封面地址                                              |
| 3516 ~ 3551   | `startPollingCloudStorageVideo()` / `stopPollingCloudStorageVideo()` — 精彩视频制作轮询（每30秒） |
| 3552 ~ 3627   | `devicesCloudStorageVideoWeek()` — 精彩视频7天列表                                        |
| 3628 ~ 3670   | `devicesCloudStorageVideoInfo()` — 精彩视频单条详情（含封面/播放地址）                    |
| 3671 ~ 3704   | `devicesCloudStorageVideoMake()` — 触发精彩视频制作                                       |
| 3705 ~ 3734   | `getDevicesCloudStorageInfo()` — 云存套餐到期时间                                         |
| 3735 ~ 3815   | `systemApp()` — 系统配置项，计算到期提醒天数                                              |
| 3816 ~ 3878   | `devicesUpgradeModulesInfo()` — 版本升级检查                                              |
| 3879 ~ 3896   | `selectDate()` / `onValueSelected()` / `onActivityResult()` — 日期回调、图表回调、页面返回结果 |

---

# 🗺️ 页面跳转入口

| 控件ID                            | 目标页面                           | 功能         |
|------------------------------     |------------------------------------|--------------|
| `right_botton`                    | `DeviceVFFeederSetActivity`        | 设备设置页   |
| `notice_lv`                       | `DeviceOutlineActivity`            | 设备概览     |
| `data_view_1 / hand_action_1`     | `DeviceVFFeederMealPlanListActivity`| 出粮计划    |
| `hand_action_2`                   | `showFeederNumDialog()`            | 手动喂食弹窗 |
| `tv_highlights`                   | `DailyHighlightsActivity`          | 每日精彩视频 |
| `tv_grain_barrel_surplus`         | `DeviceFeederSurplusActivity`      | 粮桶余量     |
| `tv_desiccant_lifespan`           | `DeviceFeederDesiccantActivity`    | 干燥剂寿命   |
| `constraint_banner1/tv_claim`     | `SubscriptionActivity`             | 套餐订阅购买 |
| `show_calendar`                   | `showCalendarDialog()`             | 日期选择     |
| `iv_start_pause`、`iv_play_back`  | `PortraitPlayActivity()`           | 日志视频播放  |
| `iv_full_screen`（CameraFragment）| `FullScreenRealTimeActivity()`     | 实时视频流播放  |

---

# 🗄️ 数据来源汇总

## 物模型透传（统一走 ApiService.devicesControl → POST /app/v1/devices/control）

**GET 查询**

| 方法名                  | propIdentifier      | resourceCategory/domain | 数据转换                                          | 更新UI/变量                                        |
|-------------------------|---------------------|-------------------------|---------------------------------------------------|----------------------------------------------------|
| `GetMachineTask()`      | `MachineTask`       | global / customDomain   | 无                                                | 无直接UI                                           |
| `GetBaterIn()`          | `BaterIn`           | global / customDomain   | Boolean                                           | mBaterIn(ImageView)、tvBatter 可见性               |
| `GetPowerMode()`        | `PowerMode`         | global / customDomain   | Boolean                                           | PowerMode变量 → changeView()、updateBaterView()    |
| `GetBatteryPercentage()`| `BatteryPercentage` | global / customDomain   | Double→int                                        | tvBatter 显示百分比                                |
| `GetKeyLockStatus()`    | `KeyLockStatus`     | global / customDomain   | Boolean                                           | KeyLockStatusSwitch 变量                           |
| `GetNightMode()`        | `NightMode`         | global / customDomain   | Double→int                                        | NightSwitch、StartTimeInt、EndTimeInt 变量         |
| `GetCancelNextMeal()`   | `CancelNextMeal`    | global / customDomain   | Boolean                                           | cancelNextMeal变量 → mCancelNext.setChecked()      |
| `GetMealPlan()`         | `MealPlan`          | global / customDomain   | List\<String\> → createPlanList() → getVFNextMealTime() | mNextFeedTime、mNextFeedDate、mFeedSize、mNoFeedTv |
| `GetLackFood()`         | `LackFood`          | global / customDomain   | Boolean                                           | tvGrainBarrelSurplusValue（充足/不足）             |
| `GetDesiccant()`        | `Desiccant`         | global / customDomain   | Double→int                                        | tvDesiccantLifespanValue（剩余X天）                |

**PUT 设置**

| 方法名                      | propIdentifier/actionIdentifier | 成功后操作                              |
|-----------------------------|---------------------------------|-----------------------------------------|
| `SetManualFeed()`           | `ManualFeed`（action）          | Toast 成功/失败                         |
| `SetCancelNextMeal(boolean)`| `CancelNextMeal`                | mCancelNext.setChecked()                |
| `SetKeyLockStatus(boolean)` | `KeyLockStatus`                 | 调用 GetKeyLockStatus() 刷新            |
| `SetNightMode()`            | `NightMode`                     | 调用 GetNightMode() 刷新                |
| `SetGeneralCmd3()`          | `GeneralCmd`（body="3"）        | 判断本地存储容量 → 走云存或本地封面分支 |
| `SetRemoteReboot()`         | `RemoteReboot`（action）        | Toast 成功/失败                         |

## REST API

| 方法名                          | ApiService接口方法                    | HTTP端点                                        | 返回Model                    | 数据转换                        | 更新UI/变量                                              |
|---------------------------------|---------------------------------------|-------------------------------------------------|------------------------------|---------------------------------|----------------------------------------------------------|
| `devicesStatus()`               | `devicesStatus()`                     | POST /app/v1/devices/status                     | `DeviceStatusModel`          | .getData().getStatus()          | status变量 → 触发 getMemberType() + initApi()            |
| `devicesInfo()`                 | `devicesInfo()`                       | POST /app/v1/devices/info                       | `DeviceInfoModel`            | .getData()                      | mCenterText、EventBus事件                                |
| `getMemberType()`               | `memberType()`                        | POST /app/v1/familyMember/memberType            | `MemberTypeModel`            | .getMemberType()                | isHavePermission → mCancelNext.setClickable()            |
| `devicesDynamicList()`          | `devicesDynamicList()`                | POST /app/v2/devicesDynamic/list                | `DevicesDynamicListModel`    | 过滤空子事件 → buildStorageIdMap() | mActionRecyclerView → loadVisibleItemCovers()         |
| `devicesExceptionStatusList()`  | `devicesExceptionStatusList()`        | POST /app/v1/devicesExceptionStatus/list        | `DevicesExceptionListModel`  | 直接赋值                        | mExceptionView → setTextSwitcherView()                   |
| `getPetInfoList()`              | `petInfoList()`                       | POST /app/v1/petInfo/list                       | `PetInfoListModel`           | clear + addAll                  | devicesDynamicListAdapter.setSinglePet()                 |
| `getOpenStatus()`               | `openStatus()`                        | POST /app/v1/devicesCloudStorage/openStatus     | `OpenStatusModel`            | .getReadState() / .getStatus()  | openStatus/serviceStatus → 触发 videoWeek() 或 productFree() |
| `getDevicesCloudStorageInfo()`  | `devicesCloudStorageInfo()`           | POST /app/v1/devicesCloudStorage/info           | `DevicesCloudStorageInfoModel`| .getExpireTime()               | 触发 systemApp(expireTime)                               |
| `systemApp(expireTime)`         | `systemApp()`                         | POST /app/v1/system/APP                         | `SystemAppModel`             | 遍历systemList，计算剩余天数    | mSrlExpirationNotice 可见性 + mStvExpirationNotice 文字  |
| `getProductFree()`              | `productFree()`                       | POST /app/v1/devicesCloudStorage/productFree    | `ProductFreeModel`           | .getData().getId() 判空         | mConstraintProbation 可见性 + mTvExperience 日期         |
| `devicesCloudStorageVideoWeek()`| `devicesCloudStorageVideoWeek()`      | POST /app/v1/devicesCloudStorage/videoWeek      | `CloudStorageVideoListModel` | 过滤 taskStatus(8/9/10)         | dailyHighlightsAdapter → startPollingCloudStorageVideo() |
| `devicesCloudStorageVideoInfo()`| `devicesCloudStorageVideoInfo()`      | POST /app/v1/devicesCloudStorage/videoInfo      | `CloudStorageVideoModel`     | .getFileUrl() / .getCoverPicUrl() | dailyHighlightsAdapter.notifyItemChanged()             |
| `getStorageDownloadUrl()`       | `storageDownloadUrl()`                | POST /app/v1/devicesCloudStorage/storageDownloadUrl | `StorageDownloadUrlModel` | .getData().getUrl() → setStorageUrl() | devicesDynamicListAdapter.notifyItemChanged(position) |
| `devicesUpgradeModulesInfo()`   | `devicesUpgradeModulesInfo()`         | POST /app/v1/devices/upgradeModulesInfo         | `DevicesUpgradeModulesModel` | type==2 且 isNeedUpgrade==1     | 弹出 UpdateVersionDialog                                 |

---

# ✅ 实现的功能

## 页面定位
喂食器主页面（带摄像头视频流），包含实时视频、设备动态、手动喂食、云存储等核心交互功能。

## 1. initApi() 调用顺序

| 序号 | 方法名                      | 说明                                   |
|------|-----------------------------|----------------------------------------|
| 1    | `GetMachineTask()`          | 查询设备工作状态                       |
| 2    | `GetBaterIn()`              | 查询电接接入状态                       |
| 3    | `GetPowerMode()`            | 查询电源模式                           |
| 4    | `GetBatteryPercentage()`    | 查询电池电量                           |
| 5    | `getActionTypeList()`       | 本地构建事件类型列表（全部/宠物/进食/出粮）|
| 6    | `devicesExceptionStatusList()`| 获取设备异常信息                     |
| 7    | `getPetInfoList()`          | 获取宠物列表                           |
| 8    | `devicesUpgradeModulesInfo()`| 版本更新检查（非日语且未显示过）       |

## 2. MealPlan 数据链路（最复杂）

```
GetMealPlan() → devicesControl GET
    ↓
data.get("data") → List<String> MealPlanList
    ↓
ModelUtils.createPlanList(MealPlanList, new ArrayList<>())
    输入: "1070800FP2" 格式字符串
    解析: enableStatus(1位) + weekEnable(2位16进制) + time(4位) + "FP" + num
    输出: List<PlanListModel>（按时间排序）
    ↓
ModelUtils.getVFNextMealTime() / getVFNextMealTime_12Hour()
    输出 Map: {type, timeStr, dateStr, num, id}
    ↓
mNextFeedTime / mNextFeedDate / mFeedSize / mNoFeedTv
```

**MealPlan 字符串格式解析：**

| 位置      | 含义                      | 示例                    |
|-----------|---------------------------|-------------------------|
| 第0位     | enableStatus（是否启用）  | 1=启用                  |
| 第1-2位   | weekEnable（16进制）      | "07" → 二进制 → 周一二三|
| 第3-6位   | time（时间）              | "0800" → 08:00          |
| "FP"后    | num（份数）               | 2                       |

## 3. 视频封面加载链路

```
devicesDynamicList() 返回列表
    ↓
buildStorageIdMap()  构建 storageId → position 映射
    ↓
loadVisibleItemCovers()  遍历可见项
    ├─ 有 storageId → getStorageDownloadUrl()
    │       → ApiService.storageDownloadUrl()
    │       → video.setStorageUrl(url) → notifyItemChanged()
    └─ 无 storageId → requestLocalCover()
            → RecordCoverFetcherManager.requestRecordCover()
            → byte[] → BitmapFactory.decodeByteArray()
            → BitmapCacheUtil 缓存（key = deviceSerial + "_" + id）
            → notifyItemChanged()
```

## 4. 云存储状态流转

```
getOpenStatus()
    ↓
openStatus（readState）= 1（已开通）
    → devicesCloudStorageVideoWeek()  获取精彩视频列表
    → startPollingCloudStorageVideo()  每30秒轮询制作状态

openStatus = 0（未开通）且有权限
    → getProductFree()  查询免费试用套餐
    → 显示 mConstraintProbation（试用入口）

getDevicesCloudStorageInfo()
    → systemApp(expireTime)
    → 计算剩余天数 → mSrlExpirationNotice（到期提醒）
```

## 5. 手动喂食流程

```
点击 hand_action_2
    ↓
showFeederNumDialog()
    → RulerView 刻度尺（范围1-20份，初始值 FeedSizeNum）
    ↓
点击提交
    ↓
SetManualFeed()
    → devicesControl(deviceOtapAction, PUT, ManualFeed, FeedSizeNum)
    ↓
code==200 → Toast "出粮成功"
code!=200 → Toast "出粮失败"
```

## 6. EventBus Socket 事件处理

| Socket 事件                          | 有无逻辑 | 触发方法                                              |
|--------------------------------------|----------|-------------------------------------------------------|
| `NextMealInfo / CancelNextMeal`      | ✅       | GetMealPlan()                                         |
| `BaterIn`                            | ✅       | GetBaterIn()                                          |
| `PowerMode`                          | ✅       | GetPowerMode()                                        |
| `DevicesOnoffline / DeviceStatusMsg` | ✅       | devicesStatus()                                       |
| `devicesExceptionStatus`             | ✅       | devicesExceptionStatusList() + devicesDynamicList() + GetMealPlan() |
| `devicesDynamic`                     | ✅       | devicesDynamicList() + GetMealPlan()                  |
| `NightMode`                          | ✅       | 更新 NightSwitch 变量                                 |
| `BatteryPercentage/KeyLockStatus/OutPutSensorStatus` | ❌ | 空 break，未实现                        |


## 7. 周选择器 + 日历弹窗数据流转

**初始化（initData 里）：**
```
doDate = sdf.format(new Date())                    // 今天日期字符串
weekModelList = DateUtil.getWeekList(mContext, doDate)
    → 以 doDate 为基准向前取6天，生成7个 WeekModel
    → 今天那格 setSelect(true)，其余 false
```

**RecyclerView 绑定：**
```
setLayoutManager(HORIZONTAL)                       // 只配置横向排列，不碰数据
weekListAdapter = new WeekListAdapter(weekModelList)
setAdapter(weekListAdapter)
smoothScrollToPosition(getItemCount() - 1)         // 滚到第6格（今天）
setSupportsChangeAnimations(false)                 // 关闭切换高亮时的闪烁动画
```

**点击某一格（权限 AND 条件）：**

| 条件                          | 结果     |
|-------------------------------|----------|
| 未开通云存 且 设备离线        | 拦截返回 |
| 未开通云存 但 设备在线        | 可点击   |
| 已开通云存（不管在不在线）    | 可点击   |

```
通过后：
doDate = model.getDate()          // 字符串，传给接口
queryDate = sdf.parse(doDate)     // Date对象，给图表/日历计算用
for 循环全部 setSelect(false) → 当前格 setSelect(true)
weekListAdapter.setList()         // 刷新高亮 UI
getActionList() → devicesDynamicList()  // 用新 doDate 拉动态列表
```

**日历弹窗（点击 show_calendar）：**
```
showCalendarDialog(doDate)
    → CalendarAdapter 加载近7个月（-6月到当前月）
    → scrollToPosition(months.size()-1)  定位当前月
    → setDefaultSelectedDate(doDate)     默认选中当前日期

点击确认后：
    ├─ 新日期在当前7格范围内
    │   → 直接更新 weekModelList 选中状态 → getActionList()
    └─ 新日期不在7格范围内（选了更早的日期）
        → DateUtil.getWeekList(mContext, doDate)  重建7格窗口
        → weekListAdapter.setList()
        → getActionList()
```



---

# ❓ 不懂的代码

## 问题 1：

**代码片段：**
```java
MealPlanList = (List<String>) data.get("data");
MealPlanList.removeIf(item -> item == null || item.isEmpty());
list = ModelUtils.createPlanList(MealPlanList, new ArrayList<>());
```

**我的疑问：**
createPlanList 第二个参数传 new ArrayList<>() 是什么意思？

**回答：**
第二个参数是服务器端的自定义喂食计划列表（devicesControlCustom 返回的数据）。在 DeviceVFFeederActivity 中 devicesControlCustom() 被注释掉了，所以直接传空列表，只用物模型返回的 MealPlanList 数据。

**我的理解（用自己的话复述）：**
createPlanList 设计上支持合并两个来源的数据（物模型 + 服务器），但这个页面只用了物模型数据，服务器那份传了个空列表。

---

## 问题 2：

**代码片段：**
```java
startPollingCloudStorageVideo()
// 每30秒轮询一次
Observable.interval(30, TimeUnit.SECONDS)
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(...)
```

**我的疑问：**
为什么精彩视频需要轮询？

**回答：**
精彩视频是后台异步制作的（devicesCloudStorageVideoMake() 触发制作任务），制作需要时间，所以需要每30秒查一次状态，直到制作完成（taskStatus 不再是"制作中"状态）才停止轮询并更新 UI。

**我的理解（用自己的话复述）：**
视频制作是异步任务，不是立刻完成的，所以要定时去问服务器"做好了吗"，做好了再刷新列表显示。

---

## 问题 3：

**代码片段：**
```java
// SetGeneralCmd3() body="3" 时
if (totalCapacity > 0) {
    if (openStatus == 1) {
        getCloudPicCoverImage(list);  // 云存封面
    } else {
        getPicCoverImage(list);       // 本地封面
    }
} else {
    getCloudPicCoverImage(list);      // 无本地存储也走云存
}
```

**我的疑问：**
为什么要先查本地存储容量再决定走哪个封面接口？

**回答：**
设备可能有 SD 卡（本地存储）也可能没有。有 SD 卡且开通了云存储，优先用云存封面（质量更好）；有 SD 卡但没开通云存，只能用本地封面；没有 SD 卡，直接走云存封面。这样做是为了在不同硬件配置下都能正确加载视频封面。

**我的理解（用自己的话复述）：**
封面来源有两个：云存储 和 本地SD卡。先查设备有没有SD卡，再结合云存开通状态，决定从哪里取封面。

---

## 问题 4：

**代码片段：**
```java
private void setTextSwitcherView(int position) {
    mTextSwitcher.setText(devicesExceptionList.get(position).getDetailsTopDes());
    mMoreBtn.setVisibility((devicesExceptionList.get(position).getUrl().equals("")
            || ModelUtils.noticeIsCanClose(devicesExceptionList.get(position).getDetailsTopKey())) ? View.GONE
            : View.VISIBLE);
    mCloseBtn.setVisibility(
            ModelUtils.noticeIsCanClose(devicesExceptionList.get(position).getDetailsTopKey()) ? View.VISIBLE
                    : View.GONE);
}
```

**我的疑问：**
`mTextSwitcher` 是什么控件？这段代码在做什么？

**回答：**
`TextSwitcher` 是 Android 的动画文字切换控件，继承自 `ViewSwitcher`。设置新文字时会有动画过渡（淡入淡出/滑动），适合轮播展示多条通知。

这个方法根据 `position` 展示一条设备异常通知，同时控制两个按钮的显隐：

| 逻辑            | 条件                        | 结果    |
|-----------------|-----------------------------|---------|
| `mMoreBtn` 隐藏 | url 为空 **或** 该通知可关闭 | GONE    |
| `mMoreBtn` 显示 | url 非空 **且** 不可关闭    | VISIBLE |
| `mCloseBtn` 显示| `noticeIsCanClose()` = true | VISIBLE |
| `mCloseBtn` 隐藏| 不可关闭                    | GONE    |

两个按钮互斥：可关闭的通知只显示关闭按钮；有跳转链接的不可关闭通知才显示"更多"按钮。

**我的理解（用自己的话复述）：**
（待填写）

---

## 问题 5：

**代码片段：**
```java
recyclerViewHighlights.setAdapter(dailyHighlightsAdapter);      // videoList
mDateRecyclerView.setAdapter(weekListAdapter);                   // weekModelList
mRecyclerActionType.setAdapter(actionTypeListAdapter);           // actionTypeModelList
mRecyclerStickyActionType.setAdapter(actionTypeTopListAdapter);  // actionTypeModelList
mActionRecyclerView.setAdapter(devicesDynamicListAdapter);       // devicesDynamicList
```

**我的疑问：**
这5个 RecyclerView 分别是干什么的，哪个是日历，哪个是动态列表？

**回答：**

| RecyclerView                | 适配器                     | 数据源               | 方向 | 用途                          |
|-----------------------------|----------------------------|----------------------|------|-------------------------------|
| `recyclerViewHighlights`    | `DailyHighlightsAdapter`   | `videoList`          | 横向 | 每日精彩视频卡片              |
| `mDateRecyclerView`         | `WeekListAdapter`          | `weekModelList`      | 横向 | 周日历（7格，点击切换日期）   |
| `mRecyclerActionType`       | `ActionTypeListAdapter`    | `actionTypeModelList`| 横向 | 事件类型筛选 Tab（普通版）    |
| `mRecyclerStickyActionType` | `ActionTypeTopListAdapter` | `actionTypeModelList`| 横向 | 事件类型筛选 Tab（吸顶版）    |
| `mActionRecyclerView`       | `DevicesDynamicListAdapter`| `devicesDynamicList` | 纵向 | 设备动态日志主列表            |

- `mDateRecyclerView` 是横向7格周选择器，在动态列表卡片顶部78dp高的一行，不是月历
- `ActionTypeListAdapter` 和 `ActionTypeTopListAdapter` 共用同一份数据，一个正常显示一个吸顶联动
- `videoList` 和 `devicesDynamicList` 完全独立，前者云存储精彩视频，后者设备行为日志

**我的理解（用自己的话复述）：**
（待填写）

---

## 问题 6：

**代码片段：**
```java
// initData() 里
doDate = sdf.format(new Date());
weekModelList = DateUtil.getWeekList(mContext, doDate);

// RecyclerView 初始化里
mDateRecyclerView.setLayoutManager(...HORIZONTAL...);
weekListAdapter = new WeekListAdapter(R.layout.item_week_list_view, weekModelList);
mDateRecyclerView.setAdapter(weekListAdapter);
mDateRecyclerView.smoothScrollToPosition(weekListAdapter.getItemCount() - 1);
```

**我的疑问：**
`setLayoutManager` 是在填充数据吗？`getItemCount() - 1` 为什么要 `-1`？

**回答：**
`setLayoutManager` 只是配置"横着排列"，不碰数据。数据在 `initData()` 里就已经准备好了。

`getItemCount() - 1`：列表下标从0开始，7个格子下标是 0~6，`getItemCount()` 返回7，最后一格（今天）位置是6，所以要 `-1`：

```
位置:  0    1    2    3    4    5    6
格子: [周一][周二][周三][周四][周五][周六][今天]
                                          ↑ getItemCount()-1 = 6
```

`smoothScrollToPosition(6)` = 带动画滚到今天；`scrollToPosition(6)` = 瞬间跳过去无动画。

`DateUtil.getWeekList()` 逻辑：以传入日期为基准，`calendar.add(DAY_OF_MONTH, -i)`（i从6到0）向前取6天，生成7个 WeekModel，今天那格 `setSelect(true)`。

**我的理解（用自己的话复述）：**
（待填写）

---

## 问题 7：

**代码片段：**
```java
((SimpleItemAnimator) mDateRecyclerView.getItemAnimator()).setSupportsChangeAnimations(false);
```

**我的疑问：**
这行是什么意思？

**回答：**
RecyclerView 默认调用 `notifyItemChanged()` 刷新某格时，会有闪烁淡入淡出动画。在周选择器里点击切换高亮时这个闪烁很难看，设成 `false` 关掉闪烁，数据变了直接刷新，视觉更干净。

```
默认(true)：点击 → 旧格闪烁消失 → 新格闪烁出现  ← 烦
设为false： 点击 → 直接切换高亮               ← 干净
```

**我的理解（用自己的话复述）：**
（待填写）

---

## 问题 8：

**代码片段：**
```java
 private void initUI() {
    weekListAdapter.setOnItemClickListener(new OnItemClickListener() {
        @Override
        public void onItemClick(BaseQuickAdapter adapter, View view, int position) {
            if (openStatus != 1 && !isDeviceStatus()) return;
            WeekModel model = (WeekModel) adapter.getData().get(position);
            doDate = model.getDate();
            for (int i = 0; i < weekModelList.size(); i++) {
                weekModelList.get(i).setSelect(false);
            }
            weekModelList.get(position).setSelect(true);
            weekListAdapter.setList(weekModelList);
            getActionList();
        }
    });
```

**我的疑问：**
为什么是在适配器上加点击监听器，而不是在 RecyclerView 上？

**回答：**
RecyclerView 本身没有 `setOnItemClickListener` 方法，这是原生 Android 的设计。这里用的是 BRVAH 库（BaseRecyclerViewAdapterHelper），`WeekListAdapter` 继承自 `BaseQuickAdapter`，该库封装好了 `setOnItemClickListener`，用起来像 ListView 一样方便。

点击逻辑流程：
1. 权限检查：未开通云存 且 设备离线 → return
2. 拿到点击格的 WeekModel → `doDate = model.getDate()`
3. 遍历 weekModelList 全部 `setSelect(false)` → 当前 position `setSelect(true)`
4. `weekListAdapter.setList()` 刷新高亮
5. `getActionList()` 用新 doDate 重新拉动态列表数据

`adapter.getData().get(position)` 是 BRVAH 提供的方法，直接从适配器内部拿数据，与 `weekModelList.get(position)` 等价。

**我的理解（用自己的话复述）：**
横向7格周选择器的点击监听挂在适配器上（BRVAH库封装），点击时先判断权限（AND条件，两个都满足才拦截）：
- 未开通云存 但设备在线 → 可以点击（能看动态列表，只是没有精彩视频）
- 开通了云存，不管在不在线 → 可以点击
- 未开通云存 且 设备离线 → 拦截

通过后拿到对应 WeekModel，更新 doDate（字符串，传给接口用）和 queryDate（Date对象，给图表/日历计算用，同一日期两种格式），for循环重置所有格的选中状态再设当前格高亮，刷新适配器UI，最后调 getActionList() 拉该日期的设备动态列表。

---

## 问题 9：日历弹窗dialog_calendar_view.xml中的recyclerView控件设置适配器、item点击回调

**代码片段：**
```java
//
RecyclerView recyclerView = contentView.findViewById(R.id.recycler_view);
recyclerView.setLayoutManager(new LinearLayoutManager(this, LinearLayoutManager.VERTICAL, false));

CalendarAdapter adapter = new CalendarAdapter();
recyclerView.setAdapter(adapter);
adapter.setOperCallBack(this);
```

**我的疑问：**
`R.id.recycler_view` 是哪个布局里的？`adapter.setOperCallBack(this)` 为什么传 `this`？

**回答：**
`R.id.recycler_view` 是 `dialog_calendar_view.xml`（弹窗布局）里的 RecyclerView 控件，通过 `contentView.findViewById()` 从已 inflate 的弹窗 View 里找到它。

`setOperCallBack(this)` 是接口回调模式：`DeviceVFFeederActivity` 实现了 `CalendarAdapter.OperCallBack` 接口，所以 Activity 本身就是 `OperCallBack` 类型，`this` 可以直接传入。用户点击日历某天时，适配器内部调用 `operCallBack.selectDate(date)`，实际执行的是 Activity 里重写的 `selectDate()` 方法，把日期传回 Activity。

BTW：`CalendarAdapter` 的 item 布局不从外面传，而是在构造函数里 `super(R.layout.item_month_calendar)` 告诉父类（BRVAH）用哪个 xml。

**我的理解（用自己的话复述）：**
 这个里面adapter.setOperCallBack(this);传入activity了，我查看这个方法是public interface OperCallBack {
void selectDate(String date);}接口，DeviceVFFeederActivity implements CalendarAdapter.OperCallBack实现了这个接口，所以这个类DeviceVFFeederActivity是OperCallBack的实现类，这里久可以用this传入。
      ↓
 之后用户点击某天
      ↓
  adapter 内部调用 operCallBack.selectDate("2026-04-15")
      ↓
  实际执行 DeviceVFFeederActivity 里重写的 selectDate() 方法
      ↓
  Activity 拿到日期，更新 doDate，刷新数据

---

## 问题 10：日历弹窗中RecyclerView控件的视图布局设置

**代码片段：**
```java
// item_month_calendar.xml 里
<TextView android:id="@+id/year_month" />   // "2026年4月" 标题
<GridLayout
    android:id="@+id/calendar_grid"
    android:columnCount="7" />              // 7列格子容器
```

**我的疑问：**
日历弹窗的 RecyclerView 里面是不是还嵌套了一个 RecyclerView？

**回答：**
不是嵌套 RecyclerView，item 里用的是 GridLayout（普通布局容器，7列）。每天的格子通过代码动态 `addView()` 塞进 GridLayout，不需要适配器。

完整层级：
```
dialog_calendar_view.xml（弹窗）
└── RecyclerView（竖向，7个月）
    └── item_month_calendar.xml × 7
        ├── TextView：显示"2026年4月"
        └── GridLayout（7列）
            └── item_day_calendar.xml × N（每天动态 inflate）
```

**我的理解（用自己的话复述）：**

---

## 问题 11：日历弹窗中选择日期后，weekModelList数据更新逻辑

**代码片段：**
```java
boolean b = false;
int position = -1;
for (int i = 0; i < weekModelList.size(); i++) {
    if (weekModelList.get(i).getDate().equals(doDate)) {
        b = true;
        position = i;
        break;
    }
}
if (!b) {
    weekModelList = DateUtil.getWeekList(mContext, doDate);
    weekListAdapter.setList(weekModelList);
    getActionList();
} else {
    // 更新高亮 + getActionList()
}
```

**我的疑问：**
日历弹窗确认后这段逻辑是在做什么？

**回答：**
检查日历选中的日期是否在当前7格窗口内，分两路处理：

- `b = false`（选了7格之外的日期，比如更早的月份）
  → 重建7格：`DateUtil.getWeekList(mContext, doDate)` 以新日期为基准重新生成7天
  → 刷新适配器 + 拉新数据

- `b = true`（选了7格内已有的日期）
  → 只更新高亮状态，不重建7格
  → 刷新适配器 + 拉新数据

**我的理解（用自己的话复述）：**
是检查weekModelList中是否有doDate，有的话b就是true，否则b=false说明选的是7格窗口之外的日期，需要重建weekModelList再更新适配器和拉数据。else分支是7格内选了其他日期，只更新高亮样式和拉新数据。

---

## 问题 12：actionTypeModelList列表创建使用全过程

**代码片段：**
```java
// 成员变量
private List<ActionTypeModel> actionTypeModelList = new ArrayList<>();
private String body = "";

//getActionList()，填充列表
actionTypeModelList.add(new ActionTypeModel(
    getString(R.string.petFeeder_common_outFeed), "3",
    body.equals("3") ? true : false)); // 出粮

// initUI() 里
actionTypeListAdapter = new ActionTypeListAdapter(
    R.layout.item_action_type_list_view, actionTypeModelList);
mRecyclerActionType.setAdapter(actionTypeListAdapter);

// initApi() 里
getActionTypeList(); // 往列表 add 4个选项

// itemClick() 里
actionTypeListAdapter.setOnItemClickListener(new OnItemClickListener() {
    public void onItemClick(BaseQuickAdapter adapter, View view, int position) {
        ActionTypeModel model = (ActionTypeModel) adapter.getData().get(position);
        for (int i = 0; i < actionTypeModelList.size(); i++) {
            actionTypeModelList.get(i).setSelect(false);
        }
        actionTypeModelList.get(position).setSelect(true); //选中
        actionTypeListAdapter.setList(actionTypeModelList);
        actionTypeTopListAdapter.setList(actionTypeModelList);
        body = model.getBody(); //存代号"1" 、"2"...
        devicesDynamicList();   //更新日志列表
    }
});
```

**我的疑问：**
`ActionTypeModel` 三个构造参数分别是什么？`body.equals("2") ? true : false` 是什么逻辑？
`getActionTypeList` 填充的是哪个列表？`adapter.getData().get(position)` 拿到的是什么？整个流程怎么串起来的？

**回答：**
`getActionTypeList()` 填充的是成员变量 `actionTypeModelList`。`adapter.getData()` 是 BRVAH 提供的方法，返回适配器内部持有的列表引用，与 `actionTypeModelList` 是同一个对象，`.get(position)` 就是取点击位置的那个 `ActionTypeModel`。

**我的理解（用自己的话复述）：**
整个流程：
1. 成员变量声明空列表 `actionTypeModelList`
2. `initUI()` 创建适配器时把列表传进去，适配器持有引用，绑定到 RecyclerView（此时列表为空）
3. `initApi()` 调用 `getActionTypeList()`，往列表 add 4个选项，body="" 初始为"全部"选中。Tab 显示出来
4. `itemClick()` 给适配器挂监听器，点击时：取出点击位置的 `ActionTypeModel` → 全部 `setSelect(false)` → 当前项 `setSelect(true)` → 刷新两个适配器改样式 → `body = model.getBody()` 存代号 → `devicesDynamicList()` 带 `categ=body` 请求后端过滤动态列表

---

## 问题 13：devicesDynamicList日志列表数据获取过程

**代码：**
```java
// devicesDynamicList() 里
 apiService.devicesDynamicList(map)
        .subscribeOn(Schedulers.io())
        .observeOn(AndroidSchedulers.mainThread())
        .subscribe(new SingleObserver<DevicesDynamicListModel>() {
            @Override
            public void onSubscribe(@NonNull Disposable d) {

            }

            @Override
            public void onSuccess(@NonNull DevicesDynamicListModel model) {
                if (model.getCode().equals("200")) {
                    if (model.getData().getTotal() > 0) {
                        mNoDataView.setVisibility(View.GONE);
                        mActionRecyclerView.setVisibility(View.VISIBLE);
                        devicesDynamicList = model.getData().getList();    //devicesDynamicList列表获取到值
...

                        buildStorageIdMap(devicesDynamicList);

                        mActionRecyclerView.post(() -> {
                            mActionRecyclerView.post(() -> loadVisibleItemCovers());   // loadVisibleItemCovers() 视频封面
                        });

// buildStorageIdMap()里
 storageIdPositionMap.put(item.getBody().getData().getVideo().getStorageId(), i);    //创建缓存 storageId -> position





```
**疑问：**
1.为什么 `devicesDynamicList() `里要用双层 post()？
2.为什么需要边界修正，这是在做什么？
3.看不懂这个`DevicesDynamicListAdapter`，一个适配器，和多个列表数据绑定？样式是不一样的，所以是怎么显示不同的样式的？




**回答：**
1.列表数据刚绑定到 adapter 时，RecyclerView 还没完成 layout pass，此时调` findFirstVisibleItemPosition() `会返回-1，封面根本不会触发。
2.找出当前屏幕上可见的 item 范围（findFirstVisibleItemPosition ~ findLastVisibleItemPosition），为展示视频封面做准备
3.不是多布局，是一个布局里藏了多个子 View，按事件类型 show/hide。


**我的理解：**


---

## 问题14：视频封面的获取，两种：云存获取，本地获取

```java

 //loadVisibleItemCovers()
    private void loadVisibleItemCovers() {
        LinearLayoutManager layoutManager = (LinearLayoutManager) mActionRecyclerView.getLayoutManager();
        if (layoutManager == null)
            return;

        int first = layoutManager.findFirstVisibleItemPosition();
        int last = layoutManager.findLastVisibleItemPosition();
        // 边界修正
        if (first < 0)
            first = 0;
        if (last >= devicesDynamicList.size())
            last = devicesDynamicList.size() - 1;

        for (int i = first; i <= last; i++) {
            DevicesDynamicListModel.DataDTO.ListDTO item = devicesDynamicList.get(i);

            if (item.getBitmap() != null)
                continue; // 已有封面，跳过

            // 云存封面
            if ("petFeeder_text_GeneralEvent".equals(item.getBody().getTitle())
                    && !android.text.TextUtils.isEmpty(item.getBody().getData().getVideo().getStorageId())
                    && openStatus == 1) {
                getStorageDownloadUrl(item.getBody().getData().getVideo().getStorageId(), i); //对应的数组位置i来更新model的云存url
            } else if (item.getBody().getData().getVideo() != null) {// 本地封面
                requestLocalCover(i);
            }
        }
    }


//DevicesDynamicListAdapter类
    if (!android.text.TextUtils.isEmpty(item.getBody().getData().getVideo().getStorageUrl())) {//云存封面
            GlideOSSLoader.loadImage(getContext(),                            //这个类如下：用来保存url的核心path，具体看疑问4
                    item.getBody().getData().getVideo().getStorageUrl(),
                    (ImageView) helper.getView(R.id.iv_play_back));
        } else if (item.getBitmap() != null) {//首帧图片（本地）
            Glide.with(getContext())
                    .load(item.getBitmap())
                    .error(R.mipmap.bg_placeholder)
                    .into((ImageView) helper.getView(R.id.iv_play_back));
        }else{
            Glide.with(getContext())          //本地和云存都没有封面显示占位图
                    .load(R.mipmap.bg_placeholder)
                    .error(R.mipmap.bg_placeholder)
                    .into((ImageView) helper.getView(R.id.iv_play_back));
}

//GlideOSSLoader类
    public static void loadImage(Context context, String url, ImageView imageView) {
        String stableKey = getStableKey(url);

        Glide.with(context)
                .load(url)
                .diskCacheStrategy(DiskCacheStrategy.ALL)
                .signature(new ObjectKey(stableKey)) // 用稳定 key 做缓存，看不懂保存时干啥
                .error(R.mipmap.bg_placeholder)
                .into(imageView);
    }

//getStorageDownloadUrl(String storageId, int position)里
    public void onSuccess(@NonNull StorageDownloadUrlModel model) {
        if ("200".equals(model.getCode()) && position >= 0 && position < devicesDynamicList.size()) {
            DevicesDynamicListModel.DataDTO.ListDTO item = devicesDynamicList.get(position);
            item.getBody().getData().getVideo().setStorageUrl(model.getData().getUrl());
            devicesDynamicListAdapter.notifyItemChanged(position);            //更新数组url
        }

//requestLocalCover()
    private void requestLocalCover(int position) {
            DevicesDynamicListModel.DataDTO.ListDTO item = devicesDynamicList.get(position);
            String cacheKey = item.getDeviceSerial() + "_" + item.getId();

            Executors.newSingleThreadExecutor().execute(() -> {
                Bitmap bitmap = BitmapCacheUtil.getBitmap(mContext, cacheKey);
                if (bitmap != null) {
                    item.setBitmap(bitmap);
                    new Handler(Looper.getMainLooper()).post(() -> devicesDynamicListAdapter.notifyItemChanged(position));
                    return;
                }

                // 没缓存才调用 requestRecordCovers
                if (item.getBody().getData().getVideo() != null) {       //这里只是空检查，不是空的，执行
                    EZDeviceRecordFile recordFile = new EZDeviceRecordFile();
                    recordFile.setSeq(position);
                    recordFile.setBegin(timestampToString(item.getBody().getData().getVideo().getStartTime()));
                    recordFile.setEnd(timestampToString(item.getBody().getData().getVideo().getEndTime()));
                    // 切换到主线程调用
                    new Handler(Looper.getMainLooper()).post(() ->
                            requestRecordCovers(Collections.singletonList(recordFile)));    //调用萤石sdk获取sd卡的视频首帧
                }
            });
        }

//requestRecordCovers()从sd卡解码视频获取到首帧
   private void requestRecordCovers(List<EZDeviceRecordFile> requestList) {
        RecordCoverFetcherManager.getInstance().requestRecordCover(requestList,
    ...
      Executors.newSingleThreadExecutor().execute(() -> {
                            Bitmap bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.length);   //解码获取Bitmap
                            if (bitmap != null) {
                                DevicesDynamicListModel.DataDTO.ListDTO cloudFile = devicesDynamicList.get(seq);
                                String cacheKey = cloudFile.getDeviceSerial() + "_" + cloudFile.getId();

                                BitmapCacheUtil.saveBitmap(mContext, cacheKey, bitmap);   //将获取到的存储到缓存中
                                cloudFile.setBitmap(bitmap);                              //DevicesDynamicListModel属性赋值

                                // 回到主线程更新 UI
                                new Handler(Looper.getMainLooper())
                                        .post(() -> devicesDynamicListAdapter.notifyItemChanged(seq));//更新列表显示封面
                            }

```
**疑问**
1.`GlideOSSLoader`类有什么作用吗？
2.在方法`getStorageDownloadUrl(String storageId, int position)`应该需要循环或则特定值，才能对应更新这个`devicesDynamicList`之前已经存在的数据，得找到映射来更新属性，这个方法里面没看到？
3.`loadVisibleItemCovers()`中`item.getBitmap()`在`requestLocalCover()`中设置`item.setBitmap(bitmap)`数据，请问这个创建Bitmap对象怎么创建的，看不懂，Bitmap bitmap = BitmapCacheUtil.getBitmap(mContext, cacheKey);？
4.那是不是在这个`requestLocalCover()`方法之前应该是有一个应该判断，要是tf卡没有，云存储没有开的话，显示默认的占位图，所以这段代码是写在哪？


**回答**

1.解决 OSS 签名 URL 缓存失效的问题。

  云存封面的 URL 是阿里云 OSS 的签名地址，长这样：
  https://xxx.oss-cn.aliyuncs.com/path/to/image.jpg?Expires=1234567&Signature=abc123...

  每次调 storageDownloadUrl 接口拿到的 URL，? 后面的签名参数都不一样（有过期时间）。

  Glide 默认用完整 URL 作为缓存 key，签名变了 → key 变了 → 缓存命中不了 → 每次都重新下载，封面加载慢还浪费流量。

  `GlideOSSLoader` 的解法：

  // 把 URL 的 query 参数去掉，只保留 path 部分作为缓存 key
  // https://xxx.oss.../path/to/image.jpg?Expires=...&Signature=...
  // → stableKey = /path/to/image.jpg
  String stableKey = uri.getPath();

  Glide.with(context)
      .load(url)                              // 实际请求还是用完整 URL（带签名，能访问）
      .signature(new ObjectKey(stableKey))    // 但缓存 key 用稳定的 path
      .diskCacheStrategy(DiskCacheStrategy.ALL)
      .into(imageView);

  结果：同一张图片，不管签名怎么换，缓存 key 始终是同一个 path，Glide 直接命中磁盘缓存，不重复下载。

2.有对应，`loadVisibleItemCovers()`中就有对应关系：`getStorageDownloadUrl(item.getBody().getData().getVideo().getStorageId(), i); `根据对应的数组位置i=[position]来更新model的云存url

3.`BitmapCacheUtil`类中创建了二级缓存，内存缓存、磁盘缓存。通过cacheKey从内存缓存中查找是否有Bitmap。没缓存Bitmap,构建`EZDeviceRecordFile recordFile`，作为参数传入到`requestRecordCovers()`方法，

流程分两条路：
 requestLocalCover(position)
    │
    ├─ BitmapCacheUtil.getBitmap() → 有缓存
    │     → item.setBitmap(bitmap)
    │     → notifyItemChanged()  ← 直接显示，结束
    │
    └─ 没缓存
          ↓
          if (video != null)  ← 这里只是空安全检查
                → 用 video.startTime / endTime 构建 EZDeviceRecordFile
                → requestRecordCovers() → 萤石SDK从SD卡取首帧
                → onGetCoverSuccess(bytes)
                      → BitmapFactory.decodeByteArray()
                      → BitmapCacheUtil.saveBitmap()  ← 存缓存
                      → item.setBitmap(bitmap)
                      → notifyItemChanged()  ← 显示出来

4.基本判断还是在load，只不过是没有分支，保持item.getBotmap()为null


**我的理解**


---


# 🔁 我能复现的逻辑
- [ ] 能独立写出：initApi() 的调用顺序和各方法的 propIdentifier
- [ ] 能独立写出：视频封面加载的双路分支逻辑（云存/本地）
- [ ] 能独立写出：手动喂食 Dialog + SetManualFeed() 的完整流程
- [ ] 还不会写：MealPlan 字符串 "1070800FP2" 的完整解析逻辑
- [ ] 还不会写：云存储状态流转（openStatus → 触发不同分支）

---

# 📌 总结

**这个类的核心逻辑一句话概括：**
> 页面初始化时并发查询设备状态（物模型 GET）和动态列表（REST API），Socket 事件驱动局部刷新，视频封面根据"有无本地存储 + 是否开通云存"走双路加载，所有设备控制统一走 `devicesControl()` 透传，云存储状态通过 `getOpenStatus() → devicesCloudStorageVideoWeek() / getProductFree()` 链式驱动 UI 展示。
