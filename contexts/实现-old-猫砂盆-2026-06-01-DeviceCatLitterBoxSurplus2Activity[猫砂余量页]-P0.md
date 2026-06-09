# 📅 日期
2026-05-20

# 📁 类名-分支名
`DeviceCatLitterBoxSurplusActivity` — `feat_v3.5.5`

# ← 来源文档

---

# 实现1.修改DeviceCatLitterBoxSurplusActivity,设备透传接口换成查询设备属性接口

## 读懂DeviceCatLitterBoxSurplus2Activity页面功能
\转换该页面
\换接口，查询设备属性接口

1.*这个helpVideo的数据是从哪里来的，
```java

    // 在 Activity 中恢复时，确保重新启动视频播放
    @Override
    protected void onResume() {
        super.onResume();
        initData();
        initUI();
        initApi();
        // 如果弹窗正在显示，重新启动视频播放
        if (centerDialog != null && centerDialog.isShowing()) {
            VideoView helpVideo = centerDialog.findViewById(R.id.help_video);
            if (!helpVideo.isPlaying()) {
                helpVideo.start();
            }
        }
    }

    // 在 Activity 中暂停时，确保暂停视频播放
    @Override
    protected void onPause() {
        super.onPause();
        // 如果弹窗正在显示，暂停视频播放
        if (centerDialog != null && centerDialog.isShowing()) {
            VideoView helpVideo = centerDialog.findViewById(R.id.help_video);
            if (helpVideo.isPlaying()) {
                helpVideo.pause();
            }
        }
    }

// initUI
//如果这里是播放，那别的地方是在干嘛呢？
 if (type == 1) {
            String videoPath = "android.resource://" + getPackageName() + "/" + R.raw.cat_litter_box_help_1; // 播放res/raw目录下的视频文件
            Uri uri = Uri.parse(videoPath);
            mToiletVideo.setVideoURI(uri);
            // 设置播放完成监听器
            mToiletVideo.setOnCompletionListener(mp -> {
                mToiletVideo.start(); // 播放完成后重新启动播放
            });
            // 启动播放
            mToiletVideo.start();
        }
```
---
2.用BaseCommonExt.kt的visibleOrGone方法

3.适配器中数据滚动，可以换成BRVAH
```java
// 模式滚动
    private void modelLinearSmoothScroll(int position) {
        // 获取 RecyclerView 并滚动到选中项
        RecyclerView recyclerView = (RecyclerView) catDeviceGoodsLitterListHAdapter.getRecyclerView();
        if (recyclerView != null) {
            LinearLayoutManager layoutManager = (LinearLayoutManager) recyclerView.getLayoutManager();
            if (layoutManager != null) {
                // 创建一个平滑滚动器，设置滚动的目标位置
                LinearSmoothScroller smoothScroller = new LinearSmoothScroller(recyclerView.getContext()) {
                    @Override
                    protected int getVerticalSnapPreference() {
                        return SNAP_TO_START; // 控制滚动后的对齐方式，这里是将目标项对齐到顶部
                    }
                };

                smoothScroller.setTargetPosition(position); // 设置目标位置
                layoutManager.startSmoothScroll(smoothScroller); // 开始平滑滚动
            }
        }

        catLitterView();
    }
```
4.点击可以换成黄油刀

```java
 // 列表点击事件
    private void itemClick() {
        catDeviceGoodsLitterListHAdapter
                .setOnItemClickListener(new com.chad.library.adapter.base.listener.OnItemClickListener() {
                    @Override
                    public void onItemClick(BaseQuickAdapter adapter, View view, int position) {
                        for (int i = 0; i < catGoodsLitterList.size(); i++) {
                            catGoodsLitterList.get(i).setSelect(false);
                        }
                        Glide.with(mContext)
                                .asBitmap() // some .jpeg files are actually gif
                                .load(catGoodsLitterList.get(position).getPic())
                                .apply(new RequestOptions()
                                        .centerCrop())
                                .into(mLitterGoodsImg);
                        mLitterGoodsName
                                .setText(ModelUtils.getTextByKey(mContext, catGoodsLitterList.get(position).getName()));
                        mLitterGoodsDes.setText(
                                ModelUtils.getTextByKey(mContext, catGoodsLitterList.get(position).getRemark()));
                        catGoodsLitterList.get(position).setSelect(true);
                        buyUrl = catGoodsLitterList.get(position).getBuyUrl();
                        curSwitchGoodName = ModelUtils.getTextByKey(mContext,
                                catGoodsLitterList.get(position).getName());
                        catDeviceGoodsLitterListHAdapter.setList(catGoodsLitterList);

                        // 获取 RecyclerView 并滚动到选中项
                        modelLinearSmoothScroll(position);
                    }
                });
    }
```
5.切换数据调用接口
```java

①    //获取关联猫砂类型
    @POST("/app/v1/devices/catLitterInfo")
    Single<DevicesCatLitterModel> devicesCatLitterInfo(@Body Map<String, Object> params);
②


   //获取关联猫砂类型
    @POST("/app/v1/devices/catLitterInfo")
    Single<DevicesCatLitterModel> devicesCatLitterInfo(@Body Map<String, Object> params);

    // // 获取设备猫砂
    private void devicesCatLitterInfo() {
        Map<String, Object> params = new HashMap<>();
        params.put("deviceSerial", device_model.getDeviceSerial());
        Map<String, Object> map = ApiClient.createParam(params);
        apiService.devicesCatLitterInfo(map)
                .subscribeOn(Schedulers.io())
                .observeOn(AndroidSchedulers.mainThread())
                .subscribe(new SingleObserver<DevicesCatLitterModel>() {
                    @Override
                    public void onSubscribe(@NonNull Disposable d) {

                    }

                    @Override
                    public void onSuccess(@NonNull DevicesCatLitterModel model) {
                        curCatLitter = model.getData().getName();
                        mCurCatLitter.setText(curCatLitter);

                        catDeviceGoodsLitterList();
                    }

                    @Override
                    public void onError(@NonNull Throwable e) {
                        Log.e("ApiService", "Error: " + e.getMessage());
                    }
                });
    }


    //    //提交关联猫砂类型
    @POST("/app/v1/devices/catLitter")
    Single<HttpSuccessModel> devicesCatLitter(@Body Map<String, Object> params);
    // 猫砂保存
    private void devicesCatLitter() {
        Map<String, Object> params = new HashMap<>();
        params.put("deviceSerial", device_model.getDeviceSerial());
        params.put("name", curCatLitter);
        Map<String, Object> map = ApiClient.createParam(params);
        apiService.devicesCatLitter(map)
                .subscribeOn(Schedulers.io())
                .observeOn(AndroidSchedulers.mainThread())
                .subscribe(new SingleObserver<HttpSuccessModel>() {
                    @Override
                    public void onSubscribe(@NonNull Disposable d) {

                    }

                    @Override
                    public void onSuccess(@NonNull HttpSuccessModel model) {
                        Gson gson = new Gson();
                        String json = gson.toJson(model); // 将 model 转换为 JSON 字符串
                        Log.e("ApiService", "Posts: " + json);

                        if (model.getCode().equals("200")) {
                            devicesCatLitterInfo();
                            catLitterView();
                        }
                    }

                    @Override
                    public void onError(@NonNull Throwable e) {
                        Log.e("ApiService", "Error: " + e.getMessage());
                    }
                });
    }

//    //设备维护列表
    @POST("/app/v1/devicesMaintenance/list")
    Single<DevicesMaintainListModel> devicesMaintainList(@Body Map<String, Object> params);

//    //设备维护（频率天数）
    @POST("/app/v1/devicesMaintenance/restDays")
    Single<HttpSuccessModel> devicesMaintainRestDays(@Body Map<String, Object> params);

//    //设备维护（复位）
    @POST("/app/v1/devicesMaintenance/rest")
    Single<HttpSuccessModel> devicesMaintainRest(@Body Map<String, Object> params);

//    //猫砂商品列表
    @POST("/app/v1/catDeviceGoods/litterList")
    Single<CatDeviceGoodsLitterListModel> catDeviceGoodsLitterList(@Body Map<String, Object> params);


```

---

//等一下，这个有些调用ApiService的不全是要替换的接口，需要查看发送请求的时候有没有发送sign签名,有的，说明是新接口，旧的接口是没有这个sign参数的.所以下面这个在DeviceCatLitterBoxSurplusActivity中的接口方法是新接口
```java

//ApiClient (com/homerunpet/engine/ApiClient.java)

 // 设备维护复位
    private void devicesMaintainRest() {
        Map<String, Object> params = new HashMap<>();
        params.put("deviceSerial", device_model.getDeviceSerial());
        params.put("eventKey", eventKey);
        Map<String, Object> map = ApiClient.createParam(params);
        apiService.devicesMaintainRest(map)
                .subscribeOn(Schedulers.io())
                .observeOn(AndroidSchedulers.mainThread())
                .subscribe(new SingleObserver<HttpSuccessModel>() {
                    @Override
                    public void onSubscribe(@NonNull Disposable d) {

                    }

                    @Override
                    public void onSuccess(@NonNull HttpSuccessModel model) {
                        CustomToast.showCustomToast(mContext, model.getMsg(), Gravity.CENTER, 0, 0, Toast.LENGTH_SHORT);
                        devicesMaintainList();
                    }

                    @Override
                    public void onError(@NonNull Throwable e) {

                    }
                });
    }


    //拼接请求参数
    public static Map<String, Object> createParam(Map<String, Object> params) {
        String timestamp = DateUtil.getTimestamp() + ""; //获取时间戳
        String signStr = paramSign(params, timestamp); //参数签名
        // 创建请求主体，使用JSON字符串作为参数
        Map<String, Object> map = new HashMap<>();
        map.put("data", params);
        map.put("timestamp", timestamp + "");
        map.put("sign", signStr);
        return map;
    }

    public static String paramSign(Map<String, Object> params, String timestamp) {
        String signStr = "";
        String appKey = Contacts.appkey;
        String paramsStr = "";

        Map<String, Object> map = new TreeMap<String, Object>(
                new Comparator<String>() {
                    public int compare(String obj1, String obj2) {
                        // 降序排序
                        return obj2.compareTo(obj1);
                    }
                });
        Set<String> keySet = params.keySet();
        Iterator<String> iter = keySet.iterator();
        while (iter.hasNext()) {
            String mapkey = iter.next();
            map.put(mapkey, params.get(mapkey));
        }
        keySet = map.keySet();
        iter = keySet.iterator();
        while (iter.hasNext()) {
            String mapkey = iter.next();
            paramsStr = paramsStr + mapkey + "=" + params.get(mapkey) + "&";
        }
        paramsStr = paramsStr + "appKey=" + appKey + "&timestamp=" + timestamp;
        signStr = SHA256Util.sha256(paramsStr);
        return signStr;
    }

    public static synchronized void reset() {
        retrofit = null;
    }
}

```

6。综上所述：我只需要改这个设备数据透传接口，其他用的都是新的接口。
①.继承HRBaseDeviceActivity,能直接调用fetchDeviceProperty，但是这里面有一层先查询有没有使用缓存，然后调用HmCommonNetUtils.fetchDeviceProperty(，
//or 继承，但直接调用接口获取数据

## 修改如下：
```java


//根据属性更新UI
    private void updateStatusView(TextView tv, ImageView img, boolean isNormal, int textNormal, int textAbnormal, int imgNormal, int imgAbnormal) {
        tv.setText(isNormal ? getText(textNormal) : getText(textAbnormal));
        tv.setTextColor(isNormal ? Color.parseColor("#383231") : Color.parseColor("#FF2742"));
        if (img != null && imgNormal != 0) {
            img.setBackgroundResource(isNormal ? imgNormal : imgAbnormal);
        }
    }

 //获取设备属性，更新UI
    private void getDeviceProperty() {
        String deviceSerial = device_model.getDeviceSerial();

        HmCommonNetUtils.fetchDeviceProperty(this, deviceSerial, new HmNetworkCallback<Map<String, Object>>() {
            @Override
            public void onSuccess(Map<String, Object> result) {
                if (result == null) return;

                Map<String, Object> data = (Map<String, Object>) result.get("data");
                if (data == null) return;

                if (result.containsKey(DevicePropertyConstants.TOILET_LITTER_STATUS)) {
                    boolean drum = Boolean.TRUE.equals(result.get(DevicePropertyConstants.TOILET_LITTER_STATUS));
                    updateStatusView(mTypeTv1, mTypeImg1, drum, R.string.catLitterBox_text_insufficientSandSilo, R.string.catLitterBox_text_insufficientSandSiloUn, R.mipmap.device_detail_20, R.mipmap.device_detail_19);
                }

                if (result.containsKey(DevicePropertyConstants.REFILL_LITTER_STATUS)) {
                    boolean sandBucket = Boolean.TRUE.equals(result.get(DevicePropertyConstants.REFILL_LITTER_STATUS));
                    updateStatusView(mTypeTv2, mTypeImg2, sandBucket, R.string.catLitterBox_text_insufficientSandFillingBucket, R.string.catLitterBox_text_insufficientSandFillingBucketUn, R.mipmap.device_detail_18, R.mipmap.device_detail_17);
                }

                if (result.containsKey(DevicePropertyConstants.WASTE_BIN_FULL_STATUS)) {
                    boolean dustbin = Boolean.TRUE.equals(result.get(DevicePropertyConstants.WASTE_BIN_FULL_STATUS));
                    updateStatusView(mTypeTv3, null, dustbin, R.string.common_text_enough, R.string.common_text_notEnough, 0, 0);
                }
            }

            @Override
            public void onError(Exception error) {
                Log.e("ApiService", "Error: " + error.getMessage());
            }
        }, false, false);
    }
```