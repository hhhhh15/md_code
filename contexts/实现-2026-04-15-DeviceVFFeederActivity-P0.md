# 📅 日期
2026-04-15

# 📁 类名-分支名
`DeviceVFFeederActivity` — `feat_v3.5.5`

# ← 来源文档
`读懂-DeviceVFFeederActivity-P0-2026-04-13.md`

---

# 🔨 实现1：ActionTypeModel 事件类型筛选 Tab 完整流程

**原始代码：**
```java
// 1. 成员变量声明
private List<ActionTypeModel> actionTypeModelList = new ArrayList<>();
private ActionTypeListAdapter actionTypeListAdapter;
private ActionTypeTopListAdapter actionTypeTopListAdapter;
private String body = ""; // 事件类型，空字符串=全部

// 2. initUI() 里绑定适配器（此时列表是空的）
mRecyclerActionType.setLayoutManager(
    new LinearLayoutManager(mContext, LinearLayoutManager.HORIZONTAL, false));
((SimpleItemAnimator) mRecyclerActionType.getItemAnimator())
    .setSupportsChangeAnimations(false);
actionTypeListAdapter = new ActionTypeListAdapter(
    R.layout.item_action_type_list_view, actionTypeModelList);
mRecyclerActionType.setAdapter(actionTypeListAdapter);

mRecyclerStickyActionType.setLayoutManager(
    new LinearLayoutManager(mContext, LinearLayoutManager.HORIZONTAL, false));
((SimpleItemAnimator) mRecyclerStickyActionType.getItemAnimator())
    .setSupportsChangeAnimations(false);
actionTypeTopListAdapter = new ActionTypeTopListAdapter(
    R.layout.item_action_type_top_list_view, actionTypeModelList);
mRecyclerStickyActionType.setAdapter(actionTypeTopListAdapter);

// 3. getActionTypeList() 填充列表（客户端写死4个选项）
private void getActionTypeList() {
    actionTypeModelList.clear();
    actionTypeModelList.add(new ActionTypeModel(
        getString(R.string.homePage_title_allRoom), "", body.isEmpty() ? true : false));   // 全部
    actionTypeModelList.add(new ActionTypeModel(
        getString(R.string.common_button_Pet), "1", body.equals("1") ? true : false));    // 宠物
    actionTypeModelList.add(new ActionTypeModel(
        getString(R.string.petFeeder_text_PetEatFood), "2", body.equals("2") ? true : false)); // 进食
    actionTypeModelList.add(new ActionTypeModel(
        getString(R.string.petFeeder_common_outFeed), "3", body.equals("3") ? true : false));  // 出粮
}

// 4. itemClick() 里给适配器挂监听器
actionTypeListAdapter.setOnItemClickListener(new OnItemClickListener() {
    @Override
    public void onItemClick(BaseQuickAdapter adapter, View view, int position) {
        ActionTypeModel model = (ActionTypeModel) adapter.getData().get(position);
        for (int i = 0; i < actionTypeModelList.size(); i++) {
            actionTypeModelList.get(i).setSelect(false);  // 全部取消选中
        }
        actionTypeModelList.get(position).setSelect(true); // 当前项选中
        actionTypeListAdapter.setList(actionTypeModelList);
        actionTypeTopListAdapter.setList(actionTypeModelList);

        body = model.getBody();   // 存下选中项的代号（"1"/"2"/"3"/""）
        devicesDynamicList();     // 带 body 作为 categ 参数请求后端
    }
});

// 5. devicesDynamicList() 里用 body 过滤
private void devicesDynamicList() {
    Map<String, Object> params = new HashMap<>();
    params.put("deviceSerial", device_model.getDeviceSerial());
    params.put("doDate", doDate);
    params.put("categ", body);   // ← body 在这里传给后端
    params.put("page", page);
    params.put("limit", limit);
    // ...
}
```

**步骤逻辑：**
1. 成员变量声明：`actionTypeModelList`（空列表）、`body`（初始为空字符串=全部）
2. `initUI()` 创建适配器并绑定到两个 RecyclerView（普通版 + 吸顶版），此时列表为空，但适配器已持有列表引用
3. `initApi()` 调用 `getActionTypeList()`，往列表里 add 4个选项，`isSelect` 根据当前 `body` 值回显选中状态
4. `itemClick()` 里给适配器挂监听器：点击时全部 `setSelect(false)` → 当前项 `setSelect(true)` → 刷新两个适配器 → `body = model.getBody()` → `devicesDynamicList()`
5. `devicesDynamicList()` 把 `body` 作为 `categ` 参数传给后端，后端按类型过滤返回动态列表

**结论：**
- [ ] 完全能独立写出
- [ ] 大体会，细节需要参考
- [ ] 还不会，需要再读一遍

**我写的代码：**
```java

```

**和原代码对比：**
- 一样的地方：
- 我写漏的：
- 我写错的：
