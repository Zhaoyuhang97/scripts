# 构建流程
> cd 项目路径下
> 
> pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
> 
> pyinstaller -D -w --icon=images/logo.gif --add-data "settings.py;." --add-data "apps;apps"  --add-data "validation.py;." --hidden-import=apps --hidden-import=settings --hidden-import=validation --hidden-import=matplotlib.backends.backend_qt5agg --hidden-import=Crypto.Cipher.AES --name tools main_window.py
>
> pyinstaller -F -w --icon=images/logo.gif --add-data "settings.py;." --add-data "apps;apps"  --add-data "validation.py;." --hidden-import=apps --hidden-import=settings --hidden-import=validation --hidden-import=matplotlib.backends.backend_qt5agg --hidden-import=Crypto.Cipher.AES --name tools main_window.py
>
> images文件夹手动拖到exe同级路径
> 