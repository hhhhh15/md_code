
# 📅 日期

2026-06-10

# 🏷️ 优先级
- [x] P0 — 马上要用到，必须搞懂
- [ ] P1 — 近期会用到
- [ ] P2 — 了解就好
- [ ] P3 — 先记录，以后再看

# 📁 类名 — 分支名

`ManualConnectionActivity` — `feat_v3.5.5`

# 🎯 本次阅读目标
    
    搞清楚手动配网比直接配网，多了什么业务步骤，是调用了接口还是什么业务。目前我看是列出产品列表，然后选择产品，可以选择手动还是ap配网。然后进入到配网页面，请问手动配网比直接配网到这个页面有什么不同的地方吗？

# ？不懂的代码

## 初始化适配器，填充数据
1.这段代码中getModel<Product>(layoutPosition) 是什么？
2.


```java
    private fun initRv() {
        val layoutManager = HoverGridLayoutManager(this, 2) // 2 则代表列表一行铺满要求跨度为2
        layoutManager.spanSizeLookup = object : GridLayoutManager.SpanSizeLookup() {
            override fun getSpanSize(position: Int): Int {
                if (position < 0) return 1 // 如果添加分割线可能导致position为负数
                // 根据类型设置列表item跨度
                return when (mBind.rv.bindingAdapter.getItemViewType(position)) {
                    R.layout.rv_item_category_product_lv1 -> 2 // 设置指定类型的跨度为1, 假设spanCount为2则代表此类型占据宽度为二分之一
                    else -> 1
                }
            }
        }
        mBind.rv.addItemDecoration(object : RecyclerView.ItemDecoration() {
            override fun getItemOffsets(
                outRect: Rect,
                view: View,
                parent: RecyclerView,
                state: RecyclerView.State
            ) {
                val position = parent.getChildAdapterPosition(view)
                if (position < 0) return

                val viewType = parent.adapter?.getItemViewType(position)

                // 只对 Product 类型 (lv2) 添加间距
                if (viewType == R.layout.rv_item_category_product_lv2) {
                    val spacing = 15.dp.toInt()
                    val spanIndex = (view.layoutParams as GridLayoutManager.LayoutParams).spanIndex

                    // 左右间距
                    if (spanIndex == 0) {
                        // 左列
                        outRect.right = spacing / 2
                    } else {
                        // 右列
                        outRect.left = spacing / 2
                    }

                    // 上下间距
                    outRect.bottom = spacing
                }
            }
        })
        mBind.rv.layoutManager = layoutManager
        mBind.rv.setup {
            addType<CategoryProductData>(R.layout.rv_item_category_product_lv1)
            addType<Product>(R.layout.rv_item_category_product_lv2)
            onBind {
                when (val data = getModel<Any>()) {
                    is CategoryProductData -> {
                        getBinding<RvItemCategoryProductLv1Binding>().apply {
                            tvTitle.text = data.name
                        }
                    }

                    is Product -> {
                        getBinding<RvItemCategoryProductLv2Binding>().apply {
                            tvSubTitle.text = data.name
                            context.preloadImage(data.icon_url)
                            ivCover.loadWithSize(data.icon_url, 32.dp.toInt(), 32.dp.toInt())
                        }
                    }
                }
            }
            R.id.sll_root.onClick {
                val model = getModel<Product>(layoutPosition)
                DeviceNetResultV2Activity.originClass = ManualConnectionActivity::class.java
                ProvisionManager.getInstance(this@ManualConnectionActivity).setProduct(model)
                ConnectionGuideActivity.launch(1)
            }
        }

        val categoryProductsSpJson = SPUtils.getInstance().getString(SPConstant.KEY_GET_PRODUCT_JSON, "")
        if (categoryProductsSpJson.isNotEmpty()) {
            runCatching {
                GsonUtils.fromJson<List<CategoryProductData?>?>(
                    categoryProductsSpJson,
                    object : TypeToken<List<CategoryProductData?>?>() {}.type
                )
            }.getOrNull()?.let { data ->
                mBind.rv.bindingAdapter.models = filterVisibleProducts(data)
            }
        }
    }
```

---

## 根据Product.is_visible过滤品类产品，这个就是页面展示数据的来源逻辑

data: List<CategoryProductData?>?结构如下：

            "category_key": "feeder",
            "name": "智能喂食器",
            "products": [
                {
                    "product_key": "gda8052e04f99490cb6826",
                    "product_model": "PF20",
                    "category_key": "feeder",
                    "name": "REAL智能喂食器",
                    "icon_url": "https://tos-homerun-prod-basic.tos-s3-cn-shanghai.volces.com/devicehub/produ

分类标题应该是调用category，也就是data.forEach { category ->中的data.name才对啊


```java

//
     * 过滤出 is_visible 为 true 的产品
     */
    private fun filterVisibleProducts(data: List<CategoryProductData?>?): List<Any> {
        if (data == null) return emptyList()

        val result = mutableListOf<Any>()
        data.forEach { category ->
            if (category != null) {
                val allProducts = category.products ?: emptyList()
                // 过滤产品列表，只保留 is_visible 为 true 的产品
                val visibleProducts = allProducts.filter { product ->
                    product?.is_visible == true
                }

                // 如果该分类下有可见的产品，才添加分类标题和产品
                if (visibleProducts.isNotEmpty()) {
                    category.products = visibleProducts
                    // 添加分类标题
                    result.add(category)
                    // 添加过滤后的产品条目
                    result.addAll(visibleProducts.filterNotNull())
                }
            }
        }
        return result
    }
```

---

# ConnectionGuideActivity

mToolbar封装的标题，位置是HMBaseActivity,com/homerunpet/v2/base/HMBaseActivity.kt

```java        
val addRightCustomLayout = mToolbar.addRightCustomLayout(R.layout.view_connect_the_device_right)
addRightCustomLayout.second.findViewById<TextView>(R.id.tv_switch).text

```


这里回调时显示点击完弹窗之后，展示选择的是蓝牙配网还是AP配网
```java
                .asCustom(GuideAttachDialog(this, isBluetoothP) { b ->
                    isBluetoothP = b //GuideAttachDialog类返回的数据结果
                    val tv = addRightCustomLayout.second.findViewById<TextView>(R.id.tv_switch)
                    if (b) {
                        tv.text = getString(R.string.provision_manual_type_ble)
                    } else if (currentPid != "A9015202") {
                        tv.text = getString(R.string.provision_manual_type_ap)
                    }
                })
                .show()


//根据isBluetoothP判断AP配网还是蓝牙配网跳转页面
            tvSubmitBtn -> {
                        if (isBluetoothP) {
                            SelectDeviceV2Activity.launch(mIsMajor)
                        } else {
                            SelectWiFiActivity.launch(0, mIsMajor)
                        }
                    }

```