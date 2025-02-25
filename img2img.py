import torch
from modelscope.utils.constant import Tasks
from modelscope.pipelines import pipeline
from modelscope.preprocessors.image import load_image
import cv2
import numpy as np
from matplotlib import pyplot as plt
import os


def detect_text_color(image):
    # 计算图像中的黑色像素和白色像素的数量
    black_pixels = np.sum(image < 50)
    white_pixels = np.sum(image > 200)
    return "black" if black_pixels > white_pixels else "white"


def save_text_image(image_path, output_path):
    # 读取图片
    image = cv2.imread(image_path)
    image = cv2.resize(image, (512, 512), interpolation=cv2.INTER_AREA)
    # 转换为灰度图像
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text_color = detect_text_color(gray[512 // 4:512 // 4 * 3, 512 // 4:512 // 4 * 3])  # 图片中心位置白色多还是黑色多来判断字体颜色
    # 使用膨胀和闭运算来连接文字的断裂部分
    # 使用自适应二值化方法
    # binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    # 自定义二值化
    # 根据文字颜色选择二值化方法
    if text_color == "white":
        # 黑底白字，先反转图像，然后二值化
        _, binary = cv2.threshold(gray, 155, 255, cv2.THRESH_BINARY_INV)
    else:
        # 白底黑字，使用普通的二值化
        _, binary = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY)

    kernel = np.ones((2, 2), np.uint8)
    dilated = cv2.dilate(binary, kernel, iterations=1)
    closed = cv2.erode(dilated, kernel, iterations=2)

    # 使用Canny边缘检测
    # closed = cv2.Canny(gray, 155, 220)  # 所有低于此阈值的边缘都会被丢弃。如果与高于highThreshold的边缘相连，这些边缘也会被保留；所有高于此阈值的边缘都会被保留

    # 使用轮廓检测来找到文字区域
    contours, _ = cv2.findContours(closed, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    # 轮廓近似
    epsilon = 0.5 * cv2.arcLength(contours[0], True)
    contours = [cv2.approxPolyDP(contour, epsilon, True) for contour in contours]

    def is_overlap(cnt1, cnt2, border=10):
        """
        合并重叠的轮廓
        Args:
            cnt1: 边界1
            cnt2: 边界2
            border: 边框距离在多少之内都算
        Returns: shape1, shape2, True or False

        """
        x1, y1, w1, h1 = cv2.boundingRect(cnt1)
        x2, y2, w2, h2 = cv2.boundingRect(cnt2)
        # return not (
        #         x1 + w1 + border <= x2 or x2 + w2 + border <= x1 or y1 + h1 + border <= y2 or y2 + h2 + border <= y1)
        if not ((200 > w1 > 20) and (200 > h1 > 20)) or not ((200 > w2 > 20) and (200 > h2 > 20)):
            return (), (), False
        return (x1, y1, w1, h1), (x2, y2, w2, h2), (
                (x1 < x2 + w2 < x1 + w1 + border) and (y1 < y2 + h2 < y1 + h1 + border)) or (
                       (x2 + w2 + border > x1 + w1 > x2) and (y2 + h2 + border > y1 + h1 > y2))

    merged_contours = []
    for now_contour in contours:
        for merged_index, merged_contour in enumerate(merged_contours):
            shape1_bounding_rect, shape2_bounding_rect, is_overlap_ = is_overlap(now_contour, merged_contour)
            if is_overlap_:
                x1, y1, w1, h1 = shape1_bounding_rect
                x2, y2, w2, h2 = shape2_bounding_rect
                x, y = min(x1, x2), min(y1, y2)
                w = max(x1 + w1, x2 + w2) - x
                h = max(y1 + h1, y2 + h2) - y
                bigger_contour = np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], dtype=np.int32)
                merged_contours[merged_index] = bigger_contour
                break
        else:
            merged_contours.append(now_contour)

    # 遍历所有合并后的轮廓并绘制矩形框
    # for contour in contours:
    old_img = os.listdir(output_path)
    for i in old_img:
        os.remove(os.path.join(output_path, i))
    for index, contour in enumerate(merged_contours):
        # 获取边界框
        x, y, w, h = cv2.boundingRect(contour)

        # 可以根据文字的大小进行过滤
        if (200 > w > 20) and (200 > h > 20):
            # 在原图上绘制边界框
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # 截图
            # cropped_image = image[y:y + h, x:x + w]
            # cropped_image_closed = closed[y:y + h, x:x + w]
            # cv2.imwrite(os.path.join(output_path, f'{index}.png'), cropped_image)
            # cv2.imwrite(os.path.join(output_path, f'{index}_gray.png'), cropped_image_closed)

    # 显示结果图像
    cv2.imshow("Text Region", image)
    cv2.imshow("Text Region2", closed)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def compare_user_image(input_image_path, image_lib_path, similarity_threshold=0.5):
    pipeline_ = pipeline(task=Tasks.multi_modal_embedding,
                         model='multi-modal_clip-vit-base-patch16_zh', model_revision='v1.0.1')
    input_images = os.listdir(input_image_path)
    input_img = [load_image(os.path.join(input_image_path, i)) for i in input_images]
    input_img_embedding = pipeline_.forward({'img': input_img})['img_embedding']  # 2D Tensor, [图片数, 特征维度]

    compare_images = os.listdir(image_lib_path)
    compare_img = [load_image(os.path.join(image_lib_path, i)) for i in compare_images]
    img_embedding = pipeline_.forward({'img': compare_img})['img_embedding']  # 2D Tensor, [图片数, 特征维度]
    #
    # # 支持一条文本(str)或多条文本(List[str])输入，输出归一化特征向量
    # text_embedding = pipeline.forward({'text': input_texts})['text_embedding']  # 2D Tensor, [文本数, 特征维度]

    # 计算图文相似度
    with torch.no_grad():
        # 计算内积得到logit，考虑模型temperature
        logits_per_image = (input_img_embedding / pipeline_.model.temperature) @ img_embedding.t()
    # 根据logit计算概率分布
    probs = logits_per_image.softmax(dim=-1).cpu().numpy()
    probs[probs < similarity_threshold] = 0
    index_max = np.argmax(probs, axis=1)
    match_images = set([compare_images[i] for i in index_max])
    # print("图文匹配概率:", probs)
    return match_images


if __name__ == '__main__':
    # user_image = "word_imgs/2c9623d8e9530105a276e9227de19f6.jpg"  # black
    # image_path = "word_imgs/61d7f31c0ba9c8782182e3b0adb2e04.jpg"  # white
    # image_path = "word_imgs/365eeb8602df455f076d6767017d216.jpg"  # white
    # image_path = "word_imgs/dc5ea4f612541f0a062facea6cdba6c.jpg"  # white
    # image_path = "word_imgs/b8bee7dcbe49dd226c3033f59d9e25b.jpg"  # white
    # image_path = "word_imgs/more.jpg"  # white
    image_path = "word_imgs/more2.jpg"  # white
    user_image_path = 'out'
    picture_lib_path = 'images'
    save_text_image(image_path=image_path, output_path=user_image_path)
    # match_image_name = compare_user_image(user_image_path, picture_lib_path)
    # for i, img_name in enumerate(match_image_name):
    #     image = cv2.imread(os.path.join(picture_lib_path, img_name))
    #     cv2.imshow(f"Text Region {i}", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()



    #########################################################################
    # for i in os.listdir(picture_lib_path):
    #     image = cv2.imread(os.path.join(picture_lib_path, i))
    #     image = cv2.resize(image, (512, 512), interpolation=cv2.INTER_AREA)
    #     # 转换为灰度图像
    #     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #     text_color = detect_text_color(gray[512 // 4:512 // 4 * 3, 512 // 4:512 // 4 * 3])  # 图片中心位置白色多还是黑色多来判断字体颜色
    #     # 使用膨胀和闭运算来连接文字的断裂部分
    #     # 使用自适应二值化方法
    #     # binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    #     # 自定义二值化
    #     # 根据文字颜色选择二值化方法
    #     if text_color == "white":
    #         # 黑底白字，先反转图像，然后二值化
    #         _, binary = cv2.threshold(gray, 155, 255, cv2.THRESH_BINARY_INV)
    #     else:
    #         # 白底黑字，使用普通的二值化
    #         _, binary = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY)
    #
    #     kernel = np.ones((2, 2), np.uint8)
    #     dilated = cv2.dilate(binary, kernel, iterations=1)
    #     closed = cv2.erode(dilated, kernel, iterations=2)
    #     cv2.imwrite(os.path.join(picture_lib_path, f"{i.split('.')[0]}_gray.{i.split('.')[1]}"), closed)


