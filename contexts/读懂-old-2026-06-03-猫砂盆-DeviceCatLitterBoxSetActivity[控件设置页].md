

这里传输的cameraDeviceModel是在接口设备详情中重组的，提取的是cameraList填充的数据
```java
          break;
            case R.id.camera_set_ll://摄像头设置
                intent = new Intent(mContext, CatLitterBoxCameraSetActivity.class);
                intent.putExtra("device_model", cameraDeviceModel);
                startActivity(intent);
                break;

                
```