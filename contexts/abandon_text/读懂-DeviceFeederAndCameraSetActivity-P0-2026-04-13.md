# 📅 日期

2026-04-13

# 🏷️ 优先级
- [x] P0 — 马上要用到，必须搞懂
- [ ] P1 — 近期会用到
- [ ] P2 — 了解就好
- [ ] P3 — 先记录，以后再看

# 📁 类名 — 分支名

`DeviceFeederAndCameraSetActivity` — `feat_v3.5.5`

# 🎯 本次阅读目标

> 这个页面是喂食器的设置页（不带视频），里面实现了哪些功能逻辑，数据从哪里来，最终展示到哪里。

---

# 🗺️ 页面跳转入口

| 控件ID | 目标页面 | 功能 |
|--------|---------|------|
| action_1 | DeviceFeederSurplusActivity | 余粮详情 |
| action_2 | DeviceFeederDesiccantActivity | 干燥剂详情 |
| action_3 | DeviceFeederMealPlanListActivity | 喂食计划列表 |
| action_4 | DeviceFeederAndCameraNightModelActivity | 夜间模式设置 |
| action_5 | DeviceMaintenanceActivity | 设备维护 |
| action_version | DeviceFeederCameraVersionListActivity | 版本升级 |
| action_use_help | DeviceUsageGuideListActivity | 使用指南 |
| action_electron | PdfActivity | 电子说明书 |
| time_zone_lv | TimeZoneActivity | 时区设置 |
| wifi_lv | DeviceFeederAndCameraWiFiActivity（有摄像头）/ HmRouterUtils.startConnectionGuide（无摄像头） | WiFi设置 |
| camera_set_ll | CameraSetActivity | 摄像头基础设置 |
| camera_operation_plan_ll | DeviceVFFeederVideoPlanListActivity | 摄像头运行计划 |
| collision_detection_set_ll | MonitorSetActivity | 监测设置 |
| push_set_ll | VFPushSetActivity | 推送设置 |
| voice_command_ll | VoiceCommandActivity | 语音指令 |
| action_subscription_service | SubscriptionActivity | 订阅服务 |
| ll_camera_place | DeviceSideboardCameraPlaceSetActivity | 识别区域设置 |
| system_reset_ll | showReset() → SetSystemReset() | 恢复出厂设置 |
| action_reboot | showRemoteReboot() → SetRemoteReboot() | 远程重启 |

---

# 🗄️ 数据来源汇总

| 数据 | 来源方法 | ApiService接口 | HTTP端点 | 返回Model |
|------|---------|---------------|---------|---------|
| 设备基本信息 | devicesInfo() | ApiService.devicesInfo() | POST /app/v1/devices/info | DeviceInfoModel |
| 设备在线状态 | devicesStatus() | ApiService.devicesStatus() | POST /app/v1/devices/status | DeviceStatusModel |
| 用户权限 | getMemberType() | ApiService.memberType() | POST /app/v1/familyMember/memberType | MemberTypeModel |
| 房间列表 | getList() | ApiService.familyRoomList() | POST /app/v1/familyRoom/list | RoomListModel |
| 待绑定摄像头 | bindList() | ApiService.bindList() | POST /app/v1/bind/list | BindListModel |
| 版本信息 | devicesUpgradeModulesInfo() | ApiService.devicesUpgradeModulesInfo() | POST /app/v1/devices/upgradeModulesInfo | DevicesUpgradeModulesModel |
| 云存储套餐 | getDevicesCloudStorageInfo() | ApiService.devicesCloudStorageInfo() | POST /app/v1/devicesCloudStorage/info | DevicesCloudStorageInfoModel |
| 所有开关/状态 | devicesControl() | ApiService.devicesControl() | POST /app/v1/devices/control | Map<String,Object> |
| 喂食计划详情 | devicesControlCustom() | ApiService.devicesControlCustom() | POST /app/v1/devices/controlCustom | devicesControlCustomListModel |
| 实时事件推送 | EventBus（Socket.IO） | — | — | MessageEvent（当前所有case为空实现） |

---

# ✅ 实现的功能

## 页面定位
喂食器（含摄像头）的设备设置页，支持喂食器单独使用，也支持绑定餐架摄像头后的联合管理。

## 1. 设备状态展示（Banner 轮播卡片）

| 状态项 | 数据来源 | 更新UI |
|--------|---------|--------|
| 设备信息卡片（喂食器+摄像头） | devicesInfo() → DeviceInfoModel | ConvenientBanner（deviceInfoList） |
| 复制SN | 点击 tv_device_id/tv_copy | ClipboardManager |
| 编辑设备名称 | CommonDialog.showNameDialog() → devicesUpdateName() | devicesInfo() 刷新 |
| 切换房间 | CommonDialog.showSelectRoomDialog() → familyRoomMoveDevices() | devicesInfo() 刷新 |
| 轮播指示器 | setupIndicators() / updateIndicators() | mLayoutIndicator（动态ImageView） |

## 2. 摄像头绑定/解绑流程

**绑定：** bindList() → showDeviceDialog() → showBindDeviceDialog() → bindDevice() → 跳转 DeviceSideboardCameraPlaceSetActivity

**解绑：** showUnbindDialog() → showUnbindDevice() → bindCancel() → devicesInfo() 刷新

## 3. 喂食器开关控制（物模型 PUT）

| Switch | propIdentifier | resourceCategory | domain |
|--------|---------------|-----------------|--------|
| mSwitch1（童锁） | KeyLockStatus | PetFeederRes | global |
| mSwitch4（摄像头开关） | VideoCtrl | global | customDomain |
| mSwitch6（堵粮感应） | BlockSensorSwitch | PetFeederRes | global |
| mSwitch7（出粮检测） | OutputSensorSwitch | PetFeederRes | global |

> 所有 Switch 用 isTouchSwitch 标志位区分用户操作和代码赋值，防止 setChecked() 触发业务逻辑。

## 4. 喂食器状态展示（物模型 GET）

| propIdentifier | resourceCategory/domain | 数据转换 | 更新UI |
|---------------|------------------------|---------|--------|
| LackFood | PetFeederRes / global | Boolean | mValue1（充足/不足） |
| Desiccant | PetFeederRes / global | Double→int | mValue2（剩余X天） |
| MealPlan | PetFeederRes / global | List\<String\> → ModelUtils.createPlanList() → getNextMealTime() | mValue3（下一餐时间） |
| NightMode | PetFeederRes / global | Double→int，+8h时区偏移，12/24h制 | mValue4（时间段或"关闭"） |
| TimerManuaFeed | PetFeederRes / global | String，按"\|"分割取第一段 | mTvRealTimeValue |
| TimeZoneCompose | PetFeederRes / TimeMgr | String | tvValueTimeZone |
| NetStatus | PetFeederRes / WifiStatus | ssid字段 | tvValueWifi（无摄像头时显示） |
| VideoCtrl | global / customDomain | Boolean | mSwitch4.setChecked() |
| BowlArea | global / customDomain | Coord1坐标判断单碗/双碗左/右 | tvCameraPlace |

## 5. 云存储套餐展示

| 条件 | 颜色 | 文字 |
|------|------|------|
| 剩余≤10天且>0 | 黄色 #FFBE6B | 到期日期 |
| 已过期≥10天 | 灰色 #999999 | 立即订阅 |
| 未开通（id==null） | — | 立即订阅 |

## 6. 设备操作

| 操作 | 流程 |
|------|------|
| 恢复出厂 | showReset() → SetSystemReset() → devicesControl(deviceOtapAction, PUT, SystemReset) |
| 远程重启 | showRemoteReboot() → SetRemoteReboot() → devicesControl(deviceOtapAction, PUT, RemoteReboot) |
| 删除设备（单设备） | CommonDialog.showConfirmDialog() → devicesDelete() → 跳转 HomeV2Activity |
| 删除设备（多设备） | showDeleteDeviceDialog() → 选择设备 → devicesDelete(deviceSerial) |

## 7. 权限与在线状态守卫

- `isHavePermissionAction()`：memberType==2 时无权限，拦截操作
- `isDeviceStatus()`：status==0 时设备离线，拦截操作
- 豁免权限检查：返回、使用帮助、电子说明书、删除、解绑
- 豁免在线检查：action_3（喂食计划，离线也可查看）

## 8. EventBus Socket 事件

所有 13 个 case（OutPutSensorStatus、MealPlan、NightMode 等）均为空 break，未实现实时推送处理。

---

# ❓ 不懂的代码

## 问题 1：

**代码片段：**
```java
mSwitch1.setOnTouchListener(new View.OnTouchListener() {
    @Override
    public boolean onTouch(View v, MotionEvent event) {
        if (!isHavePermissionAction()) return false;
        isTouchSwitch = true;
        return false;
    }
});
mSwitch1.setOnCheckedChangeListener((buttonView, isChecked) -> {
    if (isTouchSwitch) {
        isTouchSwitch = false;
        SetKeyLockStatus(isChecked);
    }
});
```

**我的疑问：**
为什么要用 isTouchSwitch 标志位，直接在 OnCheckedChangeListener 里处理不行吗？

**回答：**
因为代码调用 `setChecked()` 也会触发 `OnCheckedChangeListener`，如果不加标志位，API 返回后更新 UI 时会再次触发业务逻辑（重复发送请求）。OnTouchListener 只在用户真实触摸时触发，所以用它来标记"这次是用户操作"。

**我的理解（用自己的话复述）：**
Switch 有两种状态变化来源：用户手动拨动 和 代码 setChecked()。只有用户拨动才需要调 API，所以用 OnTouchListener 打个标记，OnCheckedChangeListener 里检查这个标记再决定要不要执行业务逻辑。

---

## 问题 2：

**代码片段：**
```java
StartTimeInt = (int) resData.get("StartTimeInt") + 8 * 3600;
EndTimeInt = (int) resData.get("EndTimeInt") + 8 * 3600;
```

**我的疑问：**
为什么要加 8 * 3600？

**回答：**
设备返回的时间是 UTC 时间（秒数），需要加 8 小时（28800秒）转换为 UTC+8 北京时间。

**我的理解（用自己的话复述）：**
设备存的是 UTC 时间，显示给用户要转成北京时间，所以加 8 小时的秒数。

---

# 🔁 我能复现的逻辑
- [ ] 能独立写出：物模型 GET/PUT 的请求参数构建方式
- [ ] 能独立写出：isTouchSwitch 防重复触发机制
- [ ] 还不会写：devicesControl() 中 Double→int 的统一转换逻辑
- [ ] 还不会写：MealPlan 字符串格式解析（"1070800FP2"）

---

# 📌 总结

**这个类的核心逻辑一句话概括：**
> 页面初始化时并发调用多个物模型 GET 接口查询设备状态，用户操作时调用物模型 PUT 接口下发指令，所有设备控制统一走 `devicesControl()` 透传方法，根据 propIdentifier 分发处理结果并更新对应 UI 控件。
