'''
FilePath: \\Image-TextRetrieval\\src\\pages\\animated_button.py
Author: ZPY
TODO: 
'''
# File: src/pages/animated_button.py
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QSize

class AnimatedButton(QPushButton):
    def __init__(self, label: str, idx: int, color: str,
                 normal_size=(220, 100),
                 hover_scale=1.2,
                 font_size=20,
                 parent=None):
        super().__init__(label, parent)
        self.idx = idx

        w, h = normal_size
        self._normal_size = QSize(w, h)
        self._hover_size = QSize(int(w*hover_scale), int(h*hover_scale))

        # 固定初始大小
        self.setMinimumSize(self._normal_size)
        self.setMaximumSize(self._normal_size)

        # 样式：背景色、白字、圆角、足够 padding 保证 hover 敏感区
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: {min(w,h)//10}px;
                padding: 10px;  /* 增加内边距，扩大 hover 区 */
            }}
        """)
        font = self.font()
        font.setPointSize(font_size)
        self.setFont(font)  # 设置字体大小

        # 大小动画，只改变最大/最小尺寸
        self._anim = QPropertyAnimation(self, b"minimumSize")
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    def enterEvent(self, event):
        # 放大到 hover 大小
        self._anim.stop()
        self._anim.setStartValue(self.size())
        self._anim.setEndValue(self._hover_size)
        self._anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        # 恢复到原始大小
        self._anim.stop()
        self._anim.setStartValue(self.size())
        self._anim.setEndValue(self._normal_size)
        self._anim.start()
        super().leaveEvent(event)
