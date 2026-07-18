# 投影片視覺設計規範（執行版）

依據 `course/00-course-plan.md` 第 6 節。全 28 頁統一適用。

## 設計哲學：每頁一個視覺焦點

一頁只有一個高對比焦點（關鍵圖解、關鍵程式碼、或關鍵一句話），
以琥珀色 `#FFB454` 標示；其餘元素降飽和、退到背景層。
觀眾視線動線：左上敘事區 → 中央焦點區 → 右下行動區。
停頓頁例外：問題置中、四周大量留白。

## 色彩

| 用途 | 色碼 |
|------|------|
| 背景 | `#171C28` 深藍黑 |
| 主文字 | `#E6E9F0` 近白 |
| 焦點強調（每頁唯一） | `#FFB454` 琥珀 |
| 次要標記 | `#5CCFE6` 青 |
| 退場元素 / 角標 | `#4A5568` 灰藍 |

## 字體

| 用途 | 字體 | 字級 |
|------|------|------|
| 標題 | Microsoft JhengHei Bold（有 Noto Sans TC Black 更佳） | 40–54 pt |
| 內文 | Microsoft JhengHei | 20–28 pt，每頁 ≤ 6 行 |
| 程式碼 | JetBrains Mono（無則 Cascadia Code / Consolas） | 16–20 pt |

## 固定版面元素

- 左下角：桑尼資料科學橫幅（PPTX 內建文字版，可換正式 logo 圖檔）
- 右下角：`© 2026 桑尼資料科學` 角標（9 pt，灰藍低對比）
- 頁碼：不做（講師自行於 PowerPoint 嵌入）

## 生圖與組版分工

- gpt-image-2（draw.py）：背景版式、圖解、icon -- 畫面不含中文字
- PowerPoint 層：所有中文文字、程式碼區塊（可編輯、零亂碼）

## 產出流程

```
python3 gen_all.py            # 寫 prompts/pNN.md + 批次生圖至 generated/
python3 build_pptx.py         # 底圖 + 中文字層 → harness-course-slides.pptx
```

生圖參數：`--size 1536x1024 --quality low`（NT$0.3/張，28 頁約 NT$9）。
封面等關鍵頁若要精緻化，刪除該頁 PNG 後以 `--quality medium` 單獨重生。

## 生圖提示詞統一風格前綴

```
Dark navy #171C28 presentation slide background, flat vector illustration style,
thin-line monochrome icons in desaturated gray-blue, single amber #FFB454 focal
element with everything else muted, generous negative space, clean grid layout,
minimal, 16:9 widescreen, no Chinese text, minimal small English labels only.
```
