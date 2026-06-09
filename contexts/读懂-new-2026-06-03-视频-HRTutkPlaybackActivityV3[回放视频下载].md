# 📅 日期

2026-06-03

# 🏷️ 优先级
- [ ] P0 — 马上要用到，必须搞懂
- [x] P1 — 近期会用到
- [ ] P2 — 了解就好
- [ ] P3 — 先记录，以后再看

# 📁 类名 — 分支名

`HRTutkPlaybackActivityV3` — `（请填写当前分支）`

# 🎯 本次阅读目标

> 搞懂 TUTK 回放页面的整体工作流：rawv 文件如何下载 → 转 MP4 → 用 ExoPlayer 播放，以及下载任务的注入与状态监听。

# 积累的知识点
> 禁止填写，用户会自己粘贴复制他认为要积累的
**概念问题**
[]1.
[]2.

---

# 分析页面代码（356 行）

## HRTutkPlaybackActivityV3（356 行）

| 行范围       | 方法名 — 说明内容                                                                                 |
|--------------|--------------------------------------------------------------------------------------------------|
| 1 ~ 55       | `companion object / 字段声明` — 静态入口 `launch()`，播放器状态字段、Handler、拖动标志位          |
| 56 ~ 100     | `gotoSwipeToDismissListener` — 下载提示条的上滑手势监听，上滑距离 > 100px 触发隐藏               |
| 101 ~ 115    | `initImmersionBar()` — 透明状态栏 + 导航栏沉浸式配置                                            |
| 116 ~ 138    | `initView()` — 初始化 DownloadRepository/ViewModel，绑定跳转下载页点击，决定是否触发下载播放     |
| 139 ~ 162    | `updateCloudVideoStatusUI()` — 根据 cloud_video_status（0封面/1正常/2过期）切换 UI 可见性         |
| 163 ~ 219    | `downloadAndPlay()` — 核心流程：缓存命中 → 跳过；否则下载 rawv → 转 MP4 → 调用 startPlay()       |
| 220 ~ 280    | `onBindViewClick()` — 播放暂停、中央播放按钮、进度条拖拽（拖动暂停静音/松手恢复）、截图/音效/下载 |
| 281 ~ 296    | `updateSoundUI()` / `updateProgress()` — 声音图标切换、进度条 + 时间文字刷新                     |
| 297 ~ 305    | `formatTime()` — 毫秒转 mm:ss 字符串                                                             |
| 306 ~ 360    | `startPlay()` — 构建 ExoPlayer，绑定 SurfaceView，注册 STATE_READY/ERROR/isPlaying 回调           |
| 361 ~ 370    | `releasePlayer()` / `takeScreenshot()` — 释放播放器；PixelCopy 截图保存到相册                    |
| 371 ~ 385    | `onPause()` / `onDestroy()` — 生命周期：暂停/释放播放器，清理 Handler 回调                       |
| 386 ~ 430    | `judgeDownload()` — 查 DB 判断任务状态，已有任务显示对应文案，无任务则调用 startDownloadV3()      |
| 431 ~ 460    | `startDownloadV3()` — 构建 DownloadTaskModel，插库后启动前台服务，注册 LiveData 监听              |
| 461 ~ 490    | `liveDataDownload()` — 观察任务状态，完成时展示下载成功提示条                                    |
| 491 ~ 530    | `showGotoDownloading()` / `showGotoCompletedWithCountdown()` — 显示提示条并启动 4 秒倒计时自动隐藏 |
| 531 ~ 556    | `startGotoCountdown()` / `cancelGotoCountdown()` / `hideGotoTip()` — 提示条倒计时管理             |
| 557 ~ 565    | `checkPermission()` — 判断 memberType == 2（子账号），无权限则 Toast 拦截                         |

**重要的代码方法**
| 116 ~ 138    | `initView()` — 初始化 DownloadRepository/ViewModel，绑定跳转下载页点击，决定是否触发下载播放     |
| 139 ~ 162    | `updateCloudVideoStatusUI()` — 根据 cloud_video_status（0封面/1正常/2过期）切换 UI 可见性         |

| 163 ~ 219    | `downloadAndPlay()` — 核心流程：缓存命中 → 跳过；否则下载 rawv → 转 MP4 → 调用 startPlay()       |
| 361 ~ 370    | `releasePlayer()` / `takeScreenshot()` — 释放播放器；PixelCopy 截图保存到相册                    |
| 386 ~ 430    | `judgeDownload()` — 查 DB 判断任务状态，已有任务显示对应文案，无任务则调用 startDownloadV3()      |
| 431 ~ 460    | `startDownloadV3()` — 构建 DownloadTaskModel，插库后启动前台服务，注册 LiveData 监听              |


---

# 🗺️ 页面控件总览

| 控件 ID                    | 功能                             | 链路 / 目标页面                        |
|----------------------------|----------------------------------|----------------------------------------|
| `flTitleBack`              | 返回按钮                         | `finish()`                             |
| `playerView`               | ExoPlayer 播放视图               | 点击切换播放 / 暂停                    |
| `ivPlayerCenterPlay`       | 中央播放图标                     | 点击播放 / 重播                        |
| `sbPlayerProgress`         | 自定义进度条                     | 拖动 seek，松手恢复播放                |
| `tvPlayerCurrentTime`      | 当前播放时间文字                 | \                                      |
| `tvPlayerTotalTime`        | 视频总时长文字                   | \                                      |
| `clPlayerLoading`          | 加载中蒙层                       | \                                      |
| `ivPlayerPlaceholder`      | 封面占位图（status=0）           | \                                      |
| `clPlayerExpired`          | 过期提示视图（status=2）         | \                                      |
| `clBottomControls`         | 底部控制栏（进度条 + 时间）       | \                                      |
| `clSideControls`           | 侧边功能栏（截图/音效/下载）      | \                                      |
| `llBtnScreenshot`          | 截图按钮                         | 调用 PixelCopy 保存相册                |
| `llBtnSound`               | 音效开关按钮                     | 切换 ExoPlayer volume                  |
| `ivPlayerSoundState`       | 音效状态图标                     | \                                      |
| `llBtnDownload`            | 下载按钮                         | 触发 `judgeDownload()`                 |
| `sllVerticalScreenGoto`    | 下载提示条（Toast 样式悬浮条）   | 点击跳转 `DownloadManagerActivity`     |
| `stvVerticalScreenGoto`    | 提示条文字                       | \                                      |

---

# 🗄️ 数据来源汇总

| 数据字段                          | 来源                                                        |
|-----------------------------------|-------------------------------------------------------------|
| `eventModel`                      | `Intent` Extra（`event_model`），由 `launch()` 传入         |
| `deviceSerial`                    | `Intent` Extra（`device_serial`）                           |
| `memberType`                      | `Intent` Extra / `SharedPreferences(curMemberType)`         |
| `cloud_video_url`                 | `eventModel.video.cloud_video_url`                          |
| `cloud_video_status`              | `eventModel.video.cloud_video_status`（0/1/2）              |
| `event_id`                        | `eventModel.event_id`，用于缓存文件命名 & DB 查询           |
| rawv 原始文件                     | OkHttp 下载到 `cacheDir/temp_{eventId}.rawv`                |
| MP4 缓存文件                      | `RawvConverter.convert()` 输出到 `cacheDir/playback_{eventId}.mp4` |
| 下载任务列表                      | `DownloadRepository.getTasksByEventAndUser()` 查本地 DB     |
| 下载任务实时状态                  | `DownloadViewModel.getTaskByIdLive()` LiveData 观察          |
| `curUserId`                       | `SharedPreferences(curUserId)`                              |

---

# ✅ 实现的功能

## 页面定位
TUTK 云端录像回放页面（V3 版）。下载 rawv 裸流 → 本地转封装为标准 MP4 → ExoPlayer 原生播放，兼顾缓存复用与下载队列管理。

---
# 页面总问题
1.      //uri的数据来源于
        private val eventModel: DeviceEventsBean? by intentExtras("event_model")、

//传入数据到下载播放方法
        val url = eventModel?.video?.cloud_video_url
        downloadAndPlay(url, eventModel?.event_id ?: "")
问题：这个eventModel的数据来源的接口是哪里？需要用cloud_video_url、event_id，数据显示是怎么样？

2.cacheDir是啥，这个File是不是存在项目里面啊？
        val mp4FileName = "playback_${eventId}.mp4"
        val mp4File = File(cacheDir, mp4FileName)

3.视频源数据mp4\m3u8\，rawv之前有说过存的结构，二进制数据，每个字节应该存储的数据内容不一样，有咩有提示？还有这个I帧关键帧很重要，所以32byte有一个I帧吗？
rawv存的数据可能有：H.265(压缩的帧数据)\
---

## 1. 视频状态分流 UI

根据 `cloud_video_status` 三态决定显示内容：

| status 值 | 含义   | UI 表现                              |
|-----------|--------|--------------------------------------|
| 0         | 无视频 | 显示封面图，隐藏控制栏               |
| 1         | 正常   | 正常显示播放器 + 控制栏，触发下载播放 |
| 2         | 过期   | 显示过期提示，隐藏控制栏             |

---

## 2. 下载 → 转码 → 播放流程（downloadAndPlay）

解码流程如下：都是在ExoPlayer播放器里面进行的
            MP4解析
              ↓
            提取H264/H265
              ↓
            MediaCodec解码
              ↓
            Surface渲染

```
检查 cacheDir/playback_{eventId}.mp4
  ├─ 存在且 > 1KB → 直接 startPlay()
  └─ 不存在
       ├─ 检查 cacheDir/temp_{eventId}.rawv
       │    └─ 不存在或 < 32B → OkHttp 下载 rawv（IO 线程）
       └─ RawvConverter.convert(rawv → mp4)（IO 线程）
            ├─ 成功 → startPlay(mp4)
            └─ 失败 → 显示错误图标
```
### downloadAndPlay方法问题


```java
 private fun downloadAndPlay(url: String, eventId: String) {
        mBind.clPlayerLoading.visible()

        lifecycleScope.launch(Dispatchers.Main) {
            try {
                // 1. 检查是否已有转换好的 MP4
                val mp4FileName = "playback_${eventId}.mp4"
//这里的File,是不是文件类啊，，看过这个方法参数是
//    public File(@RecentlyNullable File parent, @RecentlyNonNull String child) {
//     throw new RuntimeException("Stub!");
// }
                val mp4File = File(cacheDir, mp4FileName)
//1024单位是byte,所以是1kB
                if (mp4File.exists() && mp4File.length() > 1024) {
                    Log.d("V3_DEBUG", "命中 MP4 缓存，直接播放: $eventId")
                    startPlay(Uri.fromFile(mp4File))
                    return@launch
                }

                // 2. 如果没有 MP4，检查是否有原始 rawv
                val rawvFileName = "temp_${eventId}.rawv"
                val rawvFile = File(cacheDir, rawvFileName)

                if (!rawvFile.exists() || rawvFile.length() < 32) {
                    Log.d("V3_DEBUG", "开始下载原始 rawv...")
                    withContext(Dispatchers.IO) {
                        val client = OkHttpClient.Builder()
                            .connectTimeout(20, TimeUnit.SECONDS)
                            .readTimeout(120, TimeUnit.SECONDS)
                            .writeTimeout(120, TimeUnit.SECONDS)
                            .build()//构建全局使用的
//这个请求就是直接通过这个url就请求的，获取到rawv数据
                        val request = Request.Builder().url(url).build()
//execute()同步堵塞发送请求，确实这个视频流rawv的数据不能异步，enqueue()（异步）
                        client.newCall(request).execute().use { response ->
                            if (!response.isSuccessful) throw IOException("下载失败: 网络响应异常 ${response.code}")
                            val body = response.body ?: throw IOException("下载失败: 响应体为空")
//一个字节一个字节读，流式读取，
                            body.byteStream().use { input ->
//这个rawvFile是空的吗，所以是把内容加到这个里面吗？outputStream是怎么用的
//——InputStream的是读取文件。OutputStream是写入文件
//使用use能自动关闭流，防止泄露
                                rawvFile.outputStream().use { output -> input.copyTo(output) }
                            }
                        }
                    }
                }
```

---

## 3. ExoPlayer 播放控制

- **拖动进度条**：`onStartTrackingTouch` 暂停并静音，停止 Handler 刷新；`onStopTrackingTouch` seekTo + play，恢复 Handler + 音量。
- **STATE_READY 回调**：仅当用户已松手（`!mIsUserDragging`）且处于 seeking 状态时，才标记 `mIsSeeking=false` 并自动播放，防止拖动中途播放器抢先恢复。
- **进度轮询**：`mProgressRunnable` 每 1 秒刷新进度条与时间，seeking 期间跳过刷新。

### 播放器的实际使用


```java
 private fun startPlay(uri: Uri) {
        mVideoUri = uri
        releasePlayer()

        val mediaSourceFactory = DefaultMediaSourceFactory(this)

        exoPlayer = ExoPlayer.Builder(this)
            .setMediaSourceFactory(mediaSourceFactory)
            .build()
            .apply {
                // 设置为跳到最近的关键帧，实现“秒拖”效果
                setSeekParameters(SeekParameters.CLOSEST_SYNC)
                mBind.playerView.player = this
                addListener(object : Player.Listener {
                    override fun onPlaybackStateChanged(playbackState: Int) {
                        when (playbackState) {
                            Player.STATE_BUFFERING -> mBind.clPlayerLoading.visible()
                            Player.STATE_READY -> {
                                mBind.clPlayerLoading.gone()
                                // 只有当用户已经松手，且播放器跳转完毕时，才允许恢复 UI 更新和自动播放
                                if (!mIsUserDragging && mIsSeeking) {
                                    mIsSeeking = false
                                    exoPlayer?.play()
                                }
                                mHandler.post(mProgressRunnable)
                            }

                            else -> mBind.clPlayerLoading.gone()
                        }
                    }

                    override fun onPlayerError(error: PlaybackException) {
                        mBind.clPlayerLoading.gone()
                        mBind.ivPlayerCenterPlay.visible()
                    }

                    override fun onIsPlayingChanged(isPlaying: Boolean) {
                        if (isPlaying) {
                            mBind.ivPlayerCenterPlay.gone()
                            // 确保恢复播放时，进度条循环在转
                            mHandler.removeCallbacks(mProgressRunnable)
                            mHandler.post(mProgressRunnable)
                        } else {
                            if (playbackState != Player.STATE_BUFFERING) {
                                mBind.ivPlayerCenterPlay.visible()
                            }
                        }
                    }
                })
                setMediaItem(MediaItem.fromUri(uri))
                prepare()
                playWhenReady = true
            }
    }
```

//更新进度,duration，视频的整个长度；currentPosition视频的当前位置
```java
 private fun updateProgress() {
        if (mIsSeeking) return
        exoPlayer?.let { player ->
            val currentPosition = player.currentPosition
            val duration = player.duration
            if (duration > 0) {
                mBind.sbPlayerProgress.setMax(duration.toFloat())
                mBind.sbPlayerProgress.progress = currentPosition.toFloat()
                mBind.tvPlayerCurrentTime.text = formatTime(currentPosition)
                mBind.tvPlayerTotalTime.text = formatTime(duration)
            }
        }
    }

```
---

## 4. 下载任务注入（judgeDownload → startDownloadV3）

```
judgeDownload()
  ├─ DB 查任务（按 userId + eventId + fileType）
  │    ├─ 有任务 → 根据 status 显示对应文案提示条
  │    └─ 无任务 → startDownloadV3()
  
startDownloadV3()
  ├─ 构建 DownloadTaskModel（userId/eventId/url/duration 等）
  ├─ insertTask() → 启动 DownloadManagerService（前台服务）
  └─ liveDataDownload() → 观察任务完成 → showGotoCompletedWithCountdown()
```

---

## 5. 下载提示条（GotoTip）交互

- 显示时启动 4 秒倒计时自动隐藏。
- 支持上滑手势（> 100px）提前关闭。
- 点击提示条跳转 `DownloadManagerActivity`。

---

## 6. 截图

PixelCopy 从 SurfaceView 抓帧 → 转 Bitmap → `saveBitmapToGallery()`，子账号（memberType=2）无权限时拦截。

---

# ❓ 不懂的代码

> ⚠️ 禁止：CC 不得自行编造任何代码片段或问题，只复制对话中真实出现的内容

---

# 🔁 我能复现的逻辑
- [ ] 能独立写出：
- [ ] 还不会写：

---

# 📌 总结

**这个类的核心逻辑一句话概括：**

> 收到云端 rawv 录像 URL → 下载 + 本地转 MP4（有缓存则复用）→ ExoPlayer 播放，同时支持进度拖拽、截图、音效开关，以及将视频加入下载队列并实时监听下载状态。