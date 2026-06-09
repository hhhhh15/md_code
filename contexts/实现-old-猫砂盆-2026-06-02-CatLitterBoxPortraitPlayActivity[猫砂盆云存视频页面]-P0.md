# 📅 日期
2026-06-02

# 📁 类名-分支名
`` PortraitPlayActivity— `feat_v3.5.5`

# ← 来源文档
`读懂-PortraitPlayActivity-P0-2026-04-28.md`  【`CatLitterBoxPortraitPlayActivity`页面和PortraitPlayActivity是一样的啊】

---

# 🔨 实现1：cameraPlayType=2 根据
问题：
1.得捋一下这个cameraPlayType变量的赋值是在哪里
2.这个传过来的deviceSerial是猫砂盆设备的吧，还是说传过来的是400

cameraPlayType==1后面的逻辑，获取本地视频的代码都需要改掉。方法


private int cameraPlayType = 1; // 摄像头播放内容类型: 0:预览 1：本地回放  2：云回放

//onConfigurationChanged() 改了
问题，这个方法调用调用时机
initData这个方法是父类的方法，所以调用的时机是不是比本页面的其他地方都快啊，那我就在这个方法里面做判断，赋值改cameraPlayType看看有没有问题。这个onConfigurationChanged是AppCompatActivity的时候就启动了，

逻辑：电源模式并且离线，还是本地的话，会加载文案，所以要改
```java
// 切换横竖屏的样式
    @Override
    public void onConfigurationChanged(Configuration newConfig) {
        super.onConfigurationChanged(newConfig);
        judgeByPid();//改了
        AutoSize.cancelAdapt(this); // 关键：取消自动适配

        // 获取正确的LayoutParams类型（根据constraint_sv的父容器类型）
        ViewGroup.LayoutParams params = mConstraintBody.getLayoutParams();

        if (newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE) {
            isFullscreen = true;
            // 横屏模式
            params.width = ViewGroup.LayoutParams.MATCH_PARENT;
            params.height = ViewGroup.LayoutParams.MATCH_PARENT;

            // 移除原有约束（重要！）
            if (params instanceof ConstraintLayout.LayoutParams) {
                ConstraintLayout.LayoutParams constraintParams = (ConstraintLayout.LayoutParams) params;
                constraintParams.topToBottom = ConstraintLayout.LayoutParams.UNSET;
                constraintParams.topMargin = 0;
            }

            // 隐藏其他视图
            traverseAllViews(getWindow().getDecorView(), true);
            mConstraintTopFullScreen.setVisibility(View.VISIBLE);
            mConstraintBottomFullScreen.setVisibility(View.VISIBLE);
            mIvScreenshotFullScreen.setVisibility(View.VISIBLE);
            if (videoTypeList.size() == 1) {// 只有本地
                tvType2.setVisibility(View.GONE);
            } else {
                tvType2.setVisibility(View.VISIBLE);
            }

            // 强制全屏
            getWindow().addFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN);
        } else {
            isFullscreen = false;
            // 竖屏模式
            params.width = ViewGroup.LayoutParams.MATCH_PARENT;
            params.height = ConstraintLayout.LayoutParams.WRAP_CONTENT; // 或 0
//            params.height = DpOrPxUtils.dip2px(mContext, 211);

            // 恢复原有约束
            if (params instanceof ConstraintLayout.LayoutParams) {
                ConstraintLayout.LayoutParams constraintParams = (ConstraintLayout.LayoutParams) params;
                constraintParams.topToBottom = R.id.constraint_top;
                constraintParams.topMargin = DpOrPxUtils.dip2px(mContext, 131);
            }

            // 显示其他视图
            traverseAllViews(getWindow().getDecorView(), false);
            mConstraintTopFullScreen.setVisibility(View.GONE);
            mConstraintBottomFullScreen.setVisibility(View.GONE);
            mIvScreenshotFullScreen.setVisibility(View.GONE);
            if (status == 0 && cameraPlayType == 1) {// 离线+本地播放
                mConstraintPowerMode.setVisibility(View.VISIBLE);
                mConstraintLoading.setVisibility(View.GONE);
                mConstraintRight.setVisibility(View.GONE);
                mConstraintBottom.setVisibility(View.GONE);
            } else {// 智能模式
                mConstraintPowerMode.setVisibility(View.GONE);
            }

            // 退出全屏
            getWindow().clearFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN);
        }

        // 应用参数
        mConstraintBody.setLayoutParams(params);
        mConstraintBody.requestLayout();

        // 重新启用适配（保持字体不变）
        AutoSize.autoConvertDensity(this, 375, true);
    }
```

//itemClick()  没改
这个videoTypeList数组就是有问题。改了，videoModel里面只是string，boolean。填写一个进去占位，position位置就是正确的，占位的也没关系，因为UI已经被隐藏了没有调用
```java
    // 列表点击事件
    private void itemClick() {
        videoTypeListAdapter.setOnItemClickListener(new com.chad.library.adapter.base.listener.OnItemClickListener() {
            @Override
            public void onItemClick(BaseQuickAdapter<?, ?> adapter, View view, int position) {
                curPosition = position;
                for (int i = 0; i < videoTypeList.size(); i++) {
                    videoTypeList.get(i).setSelect(false);
                }
                videoTypeList.get(position).setSelect(true);
                videoTypeListAdapter.setList(videoTypeList);
                switch (position) {
                    case 0:// 本地视频
                        tvType1.setBackgroundResource(R.drawable.bg_ffffff_16);
                        tvType1.setTextColor(Color.parseColor("#383231"));
                        tvType2.setBackgroundResource(R.drawable.bg_transparent);
                        tvType2.setTextColor(Color.parseColor("#FFFFFF"));

                        // 重置播放状态
                        stopPlayVideo();
                        stopUpdateTimer();

                        // 重置进度相关
                        mRecordSecond = 0;
                        mSeekBar.setProgress(0);
                        mSeekBarFullScreen.setProgress(0);
                        mTvCurrentDuration.setText("00:00");
                        mTvCurrentDurationFullScreen.setText("00:00");
                        mTvTotalDuration.setText("00:00");
                        mTvTotalDurationFullScreen.setText("00:00");
                        Glide.with(mContext)
                                .asBitmap()
                                .load(R.mipmap.device_detail_102)
                                .into(mIvPlayFullScreen);

                        cameraPlayType = 1;
                        ivStartPause.setVisibility(View.GONE);// 暂停按钮
                        mConstraintLoading.setVisibility(View.VISIBLE);
                        if (status == 0) {// 离线
                            mConstraintPowerMode.setVisibility(View.VISIBLE);
                            mConstraintLoading.setVisibility(View.GONE);
                            mConstraintBottom.setVisibility(View.GONE);
                            mConstraintRight.setVisibility(View.GONE);
                            stopPlayVideo();
                        } else {// 在线
                            mConstraintPowerMode.setVisibility(View.GONE);
                            mConstraintBottom.setVisibility(View.VISIBLE);
                            mConstraintRight.setVisibility(View.VISIBLE);
//                            searchFileList();
                            setVideoExpiredUI();
                        }
                        break;
                    case 1:// 云存视频
                        mConstraintPowerMode.setVisibility(View.GONE);
                        tvType1.setBackgroundResource(R.drawable.bg_transparent);
                        tvType1.setTextColor(Color.parseColor("#FFFFFF"));
                        tvType2.setBackgroundResource(R.drawable.bg_ffffff_16);
                        tvType2.setTextColor(Color.parseColor("#383231"));

                        // 重置播放状态
                        stopPlayVideo();
                        stopUpdateTimer();

                        // 重置进度相关
                        mRecordSecond = 0;
                        mSeekBar.setProgress(0);
                        mSeekBarFullScreen.setProgress(0);
                        mTvCurrentDuration.setText("00:00");
                        mTvCurrentDurationFullScreen.setText("00:00");
                        mTvTotalDuration.setText("00:00");
                        mTvTotalDurationFullScreen.setText("00:00");

                        Glide.with(mContext)
                                .asBitmap()
                                .load(R.mipmap.device_detail_102)
                                .into(mIvPlayFullScreen);

                        cameraPlayType = 2;
                        ivStartPause.setVisibility(View.GONE);// 暂停按钮
                        mConstraintLoading.setVisibility(View.VISIBLE);
                        setVideoExpiredUI();// 先判断是否过期
//                        searchFileList();
                        break;
                }
            }
        });
    }
```

//initApi() 改
```java
     private void initApi() {
        videoTypeList.clear();
//        videoTypeList.add(new VideoTypeModel(getString(R.string.petFeeder_text_dynamicVideo), false));
        isCloudOnlyDevice = deviceSerial != null && deviceSerial.toUpperCase().contains("DA9128A2");
        if(isCloudOnlyDevice){
             videoTypeList.add(new VideoTypeModel(getString(R.string.petFeeder_text_localVideo), false));
            videoTypeList.add(new VideoTypeModel(getString(R.string.petFeeder_text_cloudStoredVideo), true));
            cameraPlayType = 2;

            tvType1.setVisibility(View.GONE);

            tvType2.setVisibility(View.VISIBLE);
            tvType2.setBackgroundResource(R.drawable.bg_ffffff_16);
            tvType2.setTextColor(Color.parseColor("#383231"));
        }else if (openStatus == 1 || videoExpiredStatus == 1) {// 云存视频过期状态   1:正常，2:过期
            videoTypeList.add(new VideoTypeModel(getString(R.string.petFeeder_text_localVideo), false));
            videoTypeList.add(new VideoTypeModel(getString(R.string.petFeeder_text_cloudStoredVideo), true));
            cameraPlayType = 2;

            tvType2.setBackgroundResource(R.drawable.bg_ffffff_16);
            tvType2.setTextColor(Color.parseColor("#383231"));
            tvType1.setBackgroundResource(R.drawable.bg_transparent);
            tvType1.setTextColor(Color.parseColor("#FFFFFF"));

        } else {
            videoTypeList.add(new VideoTypeModel(getString(R.string.petFeeder_text_localVideo), true));
            cameraPlayType = 1;
            tvType1.setBackgroundResource(R.drawable.bg_ffffff_16);
            tvType1.setTextColor(Color.parseColor("#383231"));
            tvType2.setBackgroundResource(R.drawable.bg_transparent);
            tvType2.setTextColor(Color.parseColor("#FFFFFF"));

            setDuration(startPlayTime, endPlayTime);
        }

        try {
            mRealPlaySh = surfaceView.getHolder();
            mRealPlaySh.addCallback(this);
            if (ApiUtils.isDomesticEnvironment()) {
                Common.saveLogToFile("国内环境");
                mEZPlayer = MyApplication.getOpenSDK().createPlayer(deviceSerial, channelNo);
            } else {
                Common.saveLogToFile("国外环境");
                mEZPlayer = MyApplication.getGlobalSDK().createPlayer(deviceSerial, channelNo);
            }
            mEZPlayer.setSurfaceHold(mRealPlaySh);
            mEZPlayer.setHandler(mHandler);
        } catch (Exception e) {
            Log.e("BaseException", e.getMessage());
            e.printStackTrace();
        }

        if (status == 0 && cameraPlayType == 1) {// 离线+本地播放
            mConstraintPowerMode.setVisibility(View.VISIBLE);
            mConstraintLoading.setVisibility(View.GONE);
            ivStartPause.setVisibility(View.GONE);
            ivPicture.setVisibility(View.GONE);
        } else {
//            searchFileList();
            mConstraintLoading.setVisibility(View.VISIBLE);
            mConstraintPowerMode.setVisibility(View.GONE);
            ivStartPause.setVisibility(View.GONE);
            ivPicture.setVisibility(View.GONE);
            setVideoExpiredUI();
        }
//        seekPlayback();
    }
```

//setVideoExpiredUI(),不用改
有云存，cameraPlayType==2的，但是云存是过期，所以隐藏加载...和那三个按钮
```JAVA
    // 视频过期(云存视频过期状态)
    private void setVideoExpiredUI() {
        if (cameraPlayType == 2 && videoExpiredStatus == 2) {
//            if (openStatus == 1 ) {//开通云存
//                if (videoExpiredStatus==2) {//视频过期
            mConstraintLoading.setVisibility(View.GONE);// 隐藏加载框
            mConstraintVideoExpired.setVisibility(View.VISIBLE);// 显示视频过期文案
            ivStartPause.setVisibility(View.GONE);
            ivPicture.setVisibility(View.GONE);
            if (isFullscreen) {
                mConstraintBottomFullScreen.setVisibility(View.GONE);
                mIvScreenshotFullScreen.setVisibility(View.GONE);
            } else {
                mConstraintRight.setVisibility(View.GONE);
                mConstraintBottom.setVisibility(View.GONE);
            }
        } else {
            mConstraintVideoExpired.setVisibility(View.GONE);// 隐藏视频过期文案
            searchFileList();
        }
    }
```



//searchFileList() 改
!(cameraPlayType == 2 && videoExpiredStatus == 2)，不满足这个条件的进入该分支
当是本地的时候，进入。 playBackVideo()，这个是文件播放
加了一个judgeByPid();//设备DAxxx
```java
  // 根据当前查询回放的模式来调用对应的方法来查询回放
    private void searchFileList() {
        mRecordSecond = 0;
        stopPlayVideo();
        judgeByPid();//设备DAxxx
        new Thread() {
            @Override
            public void run() {
                try {
                    if (cameraPlayType == 1) {
                        mEZDeviceFileList = MyApplication.getOpenSDK().searchRecordFileFromDevice(deviceSerial, channelNo, startTime, endTime);
                        Log.i("TAG本地", "deviceSerial: " + deviceSerial + "   channelNo:" + channelNo + "   startTime:" + startTime.getTime() + "   " +
                                "endTime:" + endTime.getTime());

                        Gson gson = new Gson();
                        String json = gson.toJson(mEZDeviceFileList);  // 将 model 转换为 JSON 字符串
                        Log.e("本地视频", json);
                        if (mEZDeviceFileList.size() > 0) {
                            getTotalDurationSeconds(mEZDeviceFileList.get(0));
                            if (deviceRecordFile == null) {
                                deviceRecordFile = mEZDeviceFileList.get(0);
//                                setDuration(deviceRecordFile.getBegin(), deviceRecordFile.getEnd());
                            }
                            playBackVideo();
                        } else {
                            runOnUiThread(() -> {
                                if (isFullscreen) {
                                    Toast.makeText(mContext, getString(R.string.petFeeder_text_PetEatFoodEvent_content_2), Toast.LENGTH_SHORT).show();
                                } else {
                                    CustomToast.showCustomToast(mContext, getString(R.string.petFeeder_text_PetEatFoodEvent_content_2),
                                            Gravity.CENTER, 0, 0, Toast.LENGTH_SHORT);
                                }
                                mTvTotalDuration.setText("00:00");
                                mTvTotalDurationFullScreen.setText("00:00");
                                mConstraintLoading.setVisibility(View.GONE);
                                ivStartPause.setVisibility(View.VISIBLE);
                            });
                        }

                    } 
//进入cameraPlayType == 2的云存分支
                    else {
                       /* Date queryDate = new Date();
                        //计算一天的时间
                        startTime.setTime(queryDate);
                        startTime.set(Calendar.HOUR_OF_DAY, 0);
                        startTime.set(Calendar.MINUTE, 0);
                        startTime.set(Calendar.SECOND, 0);

                        endTime.setTime(queryDate);
                        endTime.set(Calendar.HOUR_OF_DAY, 23);
                        endTime.set(Calendar.MINUTE, 59);
                        endTime.set(Calendar.SECOND, 59);*/
//萤石SDK播放器初始化
                        if (MyApplication.getOpenSDK() == null) {
                            Log.e(TAG, "EZOpenSDK is null");
                            return;
                        }
                        mCloudFileList = MyApplication.getOpenSDK().searchRecordFileFromCloud(deviceSerial, channelNo, startTime, endTime);
                        Log.i("TAG云存", "deviceSerial: " + deviceSerial + "   channelNo:" + channelNo + "   startTime:" + startTime.getTime() + "   " +
                                "endTime:" + endTime.getTime());

//                        mCloudFileList = MyApplication.getOpenSDK().searchRecordFileFromCloud("A9015601:8808F116C", channelNo, startTime, endTime);
                        Gson gson = new Gson();
                        String json = gson.toJson(mCloudFileList);  // 将 model 转换为 JSON 字符串
                        Log.i("TAG", "run:----------- " + mCloudFileList.size());
                        getTotalDurationSeconds(mCloudFileList);
                        Log.e("云存视频", json);
                        if (mCloudFileList.size() > 0) {
                            EZCloudRecordFile mergedFile = new Gson().fromJson(
                                    new Gson().toJson(mCloudFileList.get(0)),
                                    EZCloudRecordFile.class
                            );
                            mergedFile.setStartTime(mCloudFileList.get(0).getStartTime());
                            mergedFile.setStopTime(mCloudFileList.get(mCloudFileList.size() - 1).getStopTime());

                            cloudRecordFile = mergedFile;

//                            cloudRecordFile = mCloudFileList.get(0);
                            cloudRecordFile.setStartTime(mCloudFileList.get(0).getStartTime());
                            cloudRecordFile.setStopTime(mCloudFileList.get(mCloudFileList.size() - 1).getStopTime());
                            playBackVideo();
                        } else {
                            runOnUiThread(() -> {
                                if (isFullscreen) {
                                    Toast.makeText(mContext, getString(R.string.petFeeder_text_theCloudStorageVideoWasNotObtained),
                                            Toast.LENGTH_SHORT).show();
                                } else {
                                    CustomToast.showCustomToast(mContext, getString(R.string.petFeeder_text_theCloudStorageVideoWasNotObtained),
                                            Gravity.CENTER, 0, 0, Toast.LENGTH_SHORT);
                                }
                                mTvTotalDuration.setText("00:00");
                                mTvTotalDurationFullScreen.setText("00:00");
                                mConstraintLoading.setVisibility(View.GONE);
                                ivStartPause.setVisibility(View.VISIBLE);
                            });
                        }
                    }
                } catch (BaseException e) {
                    e.printStackTrace();
                }
            }
        }.start();
    }
```

//playBackVideo() 改
加了一个judgeByPid();
```java
    // 开始播放回放(文件播放)
    private void playBackVideo() {
//        MyApplication.getOpenSDK().enableP2P(true);
        Log.e("测试回放", "执行播放回放");
        judgeByPid();
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                try {
                    mRealPlaySh = surfaceView.getHolder();
                    mEZPlayer.setSurfaceHold(mRealPlaySh);
                    mEZPlayer.setHandler(mHandler);
                    new Thread(new Runnable() {
                        @Override
                        public void run() {
                            if (cameraPlayType == 1) { // 本地回放
                                if (deviceRecordFile != null) {
                                    mEZPlayer.startPlayback(deviceRecordFile);
//                                    boolean b = mEZPlayer.seekPlayback(startTime);
//                                    Log.i("TAG", "测试回放: "+b);
                                }
                            } else if (cameraPlayType == 2) { // 云回放
                                if (cloudRecordFile != null) {
                                    mEZPlayer.startPlayback(cloudRecordFile);
                                }
                            }
                        }
                    }).start();
                } catch (Exception e) {
                    Toast.makeText(mContext, "当前设备不在线", Toast.LENGTH_SHORT).show();
                    e.printStackTrace();
                }
            }
        });
    }

```


//onStopTrackingTouch() 改
seek到视频的某个位置

```java
   @Override
    public void onStopTrackingTouch(float progress) {
        judgeByPid();
        isDrag = true;// 拖动过，需要记录
        if (progress >= 100 && mEZPlayer != null) {// 拖动到最后
            isPlay = false;
            Glide.with(mContext)
                    .asBitmap()
                    .load(R.mipmap.device_detail_101)
                    .into(mIvPlayFullScreen);

            ivStartPause.setVisibility(View.VISIBLE);
            mTvCurrentDuration.setText(String.format("%02d:%02d", mTargetTime / 60, mTargetTime % 60));
            mTvCurrentDurationFullScreen.setText(String.format("%02d:%02d", mTargetTime / 60, mTargetTime % 60));

            stopUpdateTimer();
            mEZPlayer.pausePlayback();
            cloudSpeed = 1.0;
            return;
        }

        if (mEZPlayer != null) {
            mRecordSecond = (int) ((progress / 100) * mTargetTime);

            long minutes = mRecordSecond / 60;
            long seconds = mRecordSecond % 60;
            mTvCurrentDuration.setText(String.format("%02d:%02d", minutes, seconds));
            mTvCurrentDurationFullScreen.setText(String.format("%02d:%02d", minutes, seconds));

            Calendar calendar = Calendar.getInstance();
            if (cameraPlayType == 1) {// 本地回放
                if (deviceRecordFile != null) {
                    // 使用录像文件的实际开始时间
                    SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault());
                    try {
                        Date recordStartDate = sdf.parse(deviceRecordFile.getBegin());
                        Log.i(TAG, "录像开始时间: " + deviceRecordFile.getBegin());

                        calendar.setTime(recordStartDate);
                        calendar.add(Calendar.SECOND, mRecordSecond);

                        Log.i(TAG, "目标跳转时间: " + calendar.getTime());
                    } catch (ParseException e) {
                        Log.e(TAG, "解析本地录像开始时间失败", e);
                        // 降级方案：使用startTime
                        calendar.setTime(startTime.getTime());
                        calendar.add(Calendar.SECOND, mRecordSecond);
                    }
                }
            } else if (cameraPlayType == 2) {// 云存回放
                if (cloudRecordFile != null) {
                    PlayTarget playTarget = findPlayTarget(mCloudFileList, progress / 100);
                    if (playTarget != null) {
                        calendar.setTime(playTarget.file.getStartTime().getTime());
                        calendar.add(Calendar.SECOND, (int) playTarget.offsetSeconds);
                    }
                }
            }

            // 停止定时器，等待seekPlayback完成后再重启
            stopUpdateTimer();

            mConstraintLoading.setVisibility(View.VISIBLE);
            // 跳转到指定位置
            mEZPlayer.seekPlayback(calendar);

            ivStartPause.setVisibility(View.GONE);
            Glide.with(mContext)
                    .asBitmap()
                    .load(R.mipmap.device_detail_102)
                    .into(mIvPlayFullScreen);
        }
    }
```






//startDownloadDeviceVideo() 没有被引用，这个方法


猫砂盆设置主页面DeviceCatLitterBoxCameraActivity的device_model是有数据

跳转

猫砂盆的按键设置页面DeviceCatLitterBoxSetActivity的device_model