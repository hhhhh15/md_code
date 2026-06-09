

# 为View设置安全距离导航栏

这个？
```java
/**
 * 为View设置安全距离导航栏
 */
fun View.hasSafeDistanceNavigationBars(activity: Activity) {
    ViewCompat.setOnApplyWindowInsetsListener(this) { v, insets ->
        val navigationBars = insets.getInsets(WindowInsetsCompat.Type.navigationBars())
        val isImeVisible = insets.isVisible(WindowInsetsCompat.Type.ime())
        val imeHeight = insets.getInsets(WindowInsetsCompat.Type.ime()).bottom

        if (isImeVisible) {
            v.setPadding(navigationBars.left, navigationBars.top, navigationBars.right, imeHeight)
        } else {
            v.setPadding(navigationBars.left, navigationBars.top, navigationBars.right, navigationBars.bottom)
        }
        insets
    }
}
```
