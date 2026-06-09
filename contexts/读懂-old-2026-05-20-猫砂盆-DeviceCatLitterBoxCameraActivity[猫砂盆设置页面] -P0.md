# 📅 日期

2026-05-20

# 🏷️ 优先级
- [x] P0 — 马上要用到，必须搞懂
- [ ] P1 — 近期会用到
- [ ] P2 — 了解就好
- [ ] P3 — 先记录，以后再看

# 📁 类名 — 分支名

`DeviceCatLitterBoxCameraActivity` — `feat_v3.5.5`

# 🎯 本次阅读目标


# 读过的代码

### 🔨 读懂1：DeviceCatLitterBoxCameraActivity中原来的弹窗逻辑修改
铺平、补砂、展开等页面UI绑定和点击事件监听功能

**原始代码：**
```java
//1.弹窗调用
//点击按钮弹出弹窗
deviceCatLitterBoxActionAdapter.setOnItemClickListener(new OnItemClickListener() {
            @Override
            public void onItemClick(BaseQuickAdapter<?, ?> adapter, View view, int position) {
                if (!isDeviceStatus()) {
                    Toaster.show(R.string.common_text_deviceOffline);
                    return;
                }
                CatLitterActionModel.DataBean dataBean = actionList.get(position);
                switch (dataBean.getIdentifier()) {
                    case "AutomaticSand"://加砂
                        showAddNum();
                        break;
                    case "ManualShovel"://清理
                        SetManualShovel();
                        break;
                    case "ManualLayingCatLitter"://铺平
                        SetManualLayingCatLitter();
                        break;
                    case "Operate"://3-复位，4-朝上
                        if (dataBean.getName().equals(getString(R.string.catLitterBox_text_openUpwards))) {
                            SetOperate(3);
                        } else if (dataBean.getName().equals(getString(R.string.catLitterBox_text_openReset))) {
                            SetOperate(4);
                        }
                        break;
                    case "Operate_1_2"://开/关便舱门（1-开，2-关）
                        if (dataBean.getName().equals(getString(R.string.catLitterBox_text_closeBiancangGate))) {
                            SetOperate(1);
                        } else if (dataBean.getName().equals(getString(R.string.catLitterBox_text_openBiancangGate))) {
                            SetOperate(2);
                        }
                }
            }
        });
    }

//1.1.手动净味弹窗
//    /*手动净味弹窗*/
                private fun showManualDeodorizationDialog() {
                    val centerDialog = Dialog(this, R.style.BottomDialog)
                    val binding = DialogManualDeodorizationBinding.inflate(LayoutInflater.from(this))
                    centerDialog.setContentView(binding.root)

                    binding.topView.titleName.text = getString(R.string.CatLitterBoxCamera_text_odorlessMode_message8)
                    val closeBtn = binding.topView.closeBtn
                    binding.submitBtn.text = getString(R.string.common_button_confirm)

                    val data = Array(20) { i -> "${i + 1}${getString(R.string.common_text_Minute)}" }
                    var manualAirCleanNum = 2
                    binding.textPicker.minValue = 0
                    binding.textPicker.maxValue = data.size - 1
                    binding.textPicker.displayedValues = data
                    binding.textPicker.value = 1

                    binding.textPicker.setOnValueChangedListener{_,_,newVal->
                        manualAirCleanNum=newVal+1
                    }
                    closeBtn.singleClick {
                        centerDialog.cancel()
                    }

                    //点击确认发送请求，净味是Event

                }
    //1.2 补砂弹窗
                private void showAddNum() {
                Dialog centerDialog = new Dialog(mContext, R.style.BottomDialog);
                View contentView = LayoutInflater.from(mContext).inflate(R.layout.dialog_device_picker_action_view, null);
                centerDialog.setContentView(contentView);
                TextView title_name = contentView.findViewById(R.id.title_name);

                TextView cancel_btn = contentView.findViewById(R.id.cancel_btn);
                TextView submit_btn = contentView.findViewById(R.id.submit_btn);

                TextView notice_tv = contentView.findViewById(R.id.notice_tv);
                notice_tv.setVisibility(View.VISIBLE);
                notice_tv.setText(getString(R.string.catLitterBox_text_addSaidNotice));

                NumberPicker textPicker = contentView.findViewById(R.id.text_picker);

                cancel_btn.setText(getString(R.string.common_button_cancel));
                submit_btn.setText(getString(R.string.common_button_confirm));
                title_name.setText(getString(R.string.catLitterBox_title_pleaseSelectTheNumberOfSandReplenishmentParts));
                RelativeLayout closeBtn = contentView.findViewById(R.id.close_btn);

                textPicker.setDescendantFocusability(NumberPicker.FOCUS_BLOCK_DESCENDANTS);
                textPicker.setSelectedTextSize(R.dimen.dp_24);
                textPicker.setTextSize(R.dimen.dp_12);
                textPicker.setDividerColor(Color.parseColor("#00000000"));
                textPicker.setSelectedTextColor(Color.parseColor("#383231"));
                textPicker.setTextColor(Color.parseColor("#666666"));

                closeBtn.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        centerDialog.cancel();
                    }
                });

                //点击【取消】，直接关闭弹窗，不做任何操作
                cancel_btn.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        AutomaticSandNum = 1;
                        centerDialog.cancel();
                    }
                });

                //点击【确认】，下发补砂指令到设备  下发后显示toast：已下发指令到设备
                submit_btn.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View view) {
                        SetAutomaticSand(AutomaticSandNum);
                        centerDialog.cancel();
                    }
                });

                // 创建数组并用循环初始化
                String[] data = new String[3];  // 创建长度为 5 的数组
                for (int i = 0; i < 3; i++) {
                    data[i] = (i + 1) + getString(R.string.common_text_xCopies);  // 将 "1份" 到 "3份" 添加到数组中
                }

                AutomaticSandNum = 1;
                textPicker.setMinValue(0);  // 设置最小值
                textPicker.setMaxValue(data.length - 1);  // 设置最大值
                textPicker.setDisplayedValues(data);  // 设置文本数据
                textPicker.setValue(0);

                // 设置选择变化监听器
                textPicker.setOnValueChangedListener((picker, oldVal, newVal) -> {
                    AutomaticSandNum = newVal + 1;
                });

                CommonDialog.setWindow(centerDialog, Gravity.BOTTOM);
                centerDialog.show();
            }

                              

//3.获取设备详情接口，发现设备没有摄像头，不显示手动净味选项
 private void devicesInfo() { apiService.devicesInfo(map)
        .subscribeOn(Schedulers.io())
        .observeOn(AndroidSchedulers.mainThread())
        .subscribe(new SingleObserver<DeviceInfoModel>() {
            
                    @Override
                    public void onSuccess(@NonNull DeviceInfoModel model) {
                        try {
                            deviceDetails = model.getData();
                            if (device_model != null && deviceDetails != null) {
                                device_model.setDeviceName(deviceDetails.getDeviceName());
                                device_model.setPic(deviceDetails.getPic());
                                device_model.setIsBindCamera(deviceDetails.getIsBindCamera());
                                mCenterText.setText(device_model.getDeviceName());
                                if (device_model.getIsBindCamera() == 1) {//绑定摄像头
                                    currentPosition = 0;
                                } else {
                                    currentPosition = 1;
                                }
                                changeView();
                                updateIndicators(currentPosition);
                            }
                            actionList = getCatLitterBoxActionList(mContext, device_model);
                            if (model.getData() != null
                                    && model.getData().getIsBindCamera() == 0
                                    && (model.getData().getCameraList() == null || model.getData().getCameraList().isEmpty())) {
//                              mRightBotton2.setVisibility(View.VISIBLE);
                                actionList.removeIf(item -> "Manual_Deodorization".equals(item.getIdentifier()));//没有摄像头就没有手动净味

    
    
//4.添加按钮的操作列表：com/homerunpet/common/DataUtils.java
                public static List<CatLitterActionModel.DataBean> getCatLitterBoxActionList(Context mContext, DevicesModel.DataDTO.ListDTO device_model) {
                    List<CatLitterActionModel.DataBean> list = new ArrayList<>();
                    // 创建 DataBean 实例并设置对应值
                    CatLitterActionModel.DataBean valueModel1 = new CatLitterActionModel.DataBean();
                    valueModel1.setName(mContext.getString(R.string.catLitterBox_text_refillCatLitter));
                    valueModel1.setUrl(R.mipmap.device_detail_156);
                    valueModel1.setIdentifier("AutomaticSand");
                    list.add(valueModel1);

                    CatLitterActionModel.DataBean valueModel2 = new CatLitterActionModel.DataBean();
                    valueModel2.setName(mContext.getString(R.string.CLB_Detail_fundesc_ManualClean2));
                    valueModel2.setUrl(R.mipmap.device_detail_157);
                    valueModel2.setIdentifier("ManualShovel");
                    list.add(valueModel2);
                
                    if(device_model.getDeviceSerial().contains("B9012801")) {//海外猫砂盆  只有B9012801支持
                    CatLitterActionModel.DataBean valueModel3 = new CatLitterActionModel.DataBean();
                    valueModel3.setName(mContext.getString(R.string.catLitterBox_text_flatten));
                    valueModel3.setUrl(R.mipmap.device_detail_158);
                    valueModel3.setIdentifier("ManualLayingCatLitter");
                    list.add(valueModel3);
                    }....

//
```


---

**步骤逻辑：**
1.`mBind.rvBottomControls.setup`使用的BRV（BindingRecyclerView）库的 DSL 写法,rvBottomControls是Recycleview，直接就绑定UI，ActionItem里面填充的图片+文字+identifier。然后是onClick根据
    onBind {
        val binding = getBinding<ItemDeviceCatLitterBoxActionV2ViewBinding>()


---


---