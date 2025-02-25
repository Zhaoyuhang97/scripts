import fitz  # PyMuPDF 的别名
import os

# 输入 PDF 文件路径
pdf_path = r'C:\Users\kmsj845\OneDrive - AZCollaboration\Desktop\机器人相关\1\科目三笔记-水印.pdf'

# 输出图片保存的文件夹路径
output_folder = r'C:\Users\kmsj845\OneDrive - AZCollaboration\Desktop\机器人相关\1f'

# 创建输出文件夹（如果不存在）
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 打开 PDF 文件
doc = fitz.open(pdf_path)

# 遍历每一页并将其转换为图片
for page_num in range(len(doc)):
    page = doc.load_page(page_num)  # 加载页面
    pix = page.get_pixmap(dpi=300)  # 获取页面的像素数据

    # 保存为 PNG 图片
    image_path = os.path.join(output_folder, f"page_{page_num + 1}.png")
    pix.save(image_path)
    print(f"Saved {image_path}")

print("All pages have been converted to images.")

