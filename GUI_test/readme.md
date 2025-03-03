# 构建流程
> cd 项目路径下
> 
> pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
>
> pyinstaller -F -w --icon=images/logo.gif --contents-directory "." --add-data "apps;apps" --hidden-import=apps --hidden-import=matplotlib.backends.backend_qt5agg --hidden-import=Crypto.Cipher.AES --name tools main_window.py
>
> images文件夹手动拖到exe同级路径
> 