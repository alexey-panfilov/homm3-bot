"""
Download Reference Screenshots from HoMM3 HD

Downloads gameplay screenshots to use for UI element extraction.
"""

import sys
from pathlib import Path
import requests
from PIL import Image
from io import BytesIO

# Screenshot URLs from HoMM3 HD+ screenshots page
SCREENSHOT_URLS = [
    "https://lh3.googleusercontent.com/sitesv/APaQ0SQjD_Vc3xk67I2tIn-rI-uWXjvGT3WxXcATYazVMr-Qvov8eSF9ZCxLer_75iLZy6pVZ0MsMlpsKHnK7wddDMGFzXjfDNuvlS8jMW0XAX79OKFwaockCZwYJ0ZJPD6Z1jLEzWRvJ52FbUr64GtnV3ejK79l_JwBsBun-1Bm2Aq9dJq8XIpscmJFt6bkawqimxQNgDRujtb33I38SgCevWO4lsNmfIFftSsa=w1280",
    "https://lh3.googleusercontent.com/sitesv/APaQ0STZ0nkxnwu7zEf6CY1W_tDrJOedytCYesIWk7sD-t9JqpXsred5-eLaQCUHCl3dfhD6KBQSlDChq85vDd2PyWFtJn7GJTzzrRZAfcUrSKHfWjEKEGgP0atdFZS7NPVUHOWXMi5NaXVqu07ALuHT4RznGqJiljvoBCnIUP9xNPWPp7-j4cPmbUV0Eoy_ixOZSvuaa2U91MoWr9CqCEyXQh8qyqZqL-5a_Y8f3-o=w1280",
    "https://lh3.googleusercontent.com/sitesv/APaQ0STlJ2FNYzajibcUkm42JOp9f6fsDU2Mqild7mlzLlqc3zVIVqOIV7Rg0IYyVXr7J-MUTb_ujl76ouRG8UyHumGIy7Z_Wd5NDVYXWj6vGgzGtUyUA3nsj43UhcFY6-yOtoucoBjXx-RhlKKJj152jONkKWmWshzMmWlJhf0WnfgvciX5eCv1esgJhwELpfodTC58Mn3m5nTYMc6mNyEhtLEx9L89dGXZ3crZN-Y=w1280",
    "https://lh3.googleusercontent.com/sitesv/APaQ0STgaUjZCGPsbcUji0-gWeve7Y_c42HdcuSkY7eya8VMZdfGfWyMCwqBK0MtgJrmp0ro2D6FuK_Qf3KGL5wIFynSTelFEhXVXW9WJ1pXgHDMmVY2evxIOkjAMBpviI9O0M-RupkBRffqACn427pcHEkfIYF7TFqj7lXEhHzXs-n4h5M1g3sFGFetIBqdp9ZcvAgiAshZMioFdC2bLTKLq0k46JBk7lHT0KRdy04=w1280",
    "https://lh3.googleusercontent.com/sitesv/APaQ0SRUIHSk2979t02CGUOxyldiKkSkAj_jxZkNofSSrKpBdp_2wa7M0tqNG-gYLFwXbJI3bJExUza8GXyxsrpCfUBkCrky2CsnSDGv8RV3asw4g2sja5QhrNkTCGEPZYdKsuSyk_mOew5V4Nzn9ZHi9OwjpAU8uw0FcPzkTmlMzCxShladj-3rcsMbl6zX2w1yS8KkbX1GnzrOyd4H9cbH7DnTph2_83vVj156=w1280",
    "https://lh3.googleusercontent.com/sitesv/APaQ0SSadFggRJdwpT-NGc2gRjQ_ayY3UXFdYFvts2V_g67_0mBLjOazUHjvhV_mTW7zbqwWHtRlLBT6mcGOQmQlfnl0Oa-K1X0d7HvrD6IMB5fvahUEt0lVdigpsNDwplPQyHlVm0KL6mUN9btayXwOalGDC7lfRv60VzG_zXfGgPR05_USC7Lk6VP-uKnSkQdoh52TQ_GmWvMoJheGqR7MWB1sRkN-Cy0dOl1Z530=w1280",
    "https://lh3.googleusercontent.com/sitesv/APaQ0SRsRODnni3zBihJ07ORB0O8_fxfn1LtfMoaWLFmSgYHpa7o_W1slCImMRPcdsNGXVq6FRUoufYuJYXU_CHkgOnK4-W0LBY9y8adN8QxKhB29tNC-RqSSPd7i6qvixISd0rLyplmvJgYCPuktezvAMzHPSwGPDoZ4DdO0aJ1eJ2_tZKqo63uP1dml89wG2w0eYWy09LbWOYqq6HD_kH45Djjqd49fUe0yNksEkw=w1280",
    "https://lh3.googleusercontent.com/sitesv/APaQ0SRPjH7w7Gd9G148GtlSAm2mEt0Px4LWv_PoY6C8AO_UhwJmvOMwEQxbqaeA2JDZrVIrskINWP_Ut5FlR1bn3N6Xd--2u-nHDKO4F2XIF6M5X3q_bycrpkJ4twaD2zPxRz-A2iSm3WiD8wBPDvKGskEdTfa0-n21kduoFDIV_HLuiDeTHWTO-BeHJ-oeKhOWyh0d-LPjYqwSNn5r1j6uh_QcGRvtyZ0SRP7s23w=w1280",
]

print("=" * 70)
print("Downloading HoMM3 HD Reference Screenshots")
print("=" * 70)
print()

# Create output directory in scratchpad
output_dir = Path(r"C:\Users\alexe\AppData\Local\Temp\claude\c--Users-alexe-Caude\44a5218a-0d8a-4941-a9c7-8c861e20d904\scratchpad\homm3_screenshots")
output_dir.mkdir(parents=True, exist_ok=True)

print(f"Output directory: {output_dir}")
print(f"Downloading {len(SCREENSHOT_URLS)} screenshots...")
print()

downloaded = 0
failed = 0

for i, url in enumerate(SCREENSHOT_URLS, 1):
    print(f"[{i}/{len(SCREENSHOT_URLS)}] Downloading screenshot {i}...", end=" ")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Open image and save
        img = Image.open(BytesIO(response.content))

        # Save with descriptive name
        output_path = output_dir / f"homm3_hd_ref_{i:02d}.png"
        img.save(output_path, "PNG")

        print(f"OK ({img.size[0]}x{img.size[1]})")
        downloaded += 1

    except Exception as e:
        print(f"FAILED - {str(e)}")
        failed += 1

print()
print("=" * 70)
print("Download Complete!")
print("=" * 70)
print()
print(f"Successfully downloaded: {downloaded}")
print(f"Failed: {failed}")
print()
print(f"Screenshots saved to: {output_dir}")
print()
print("Next step: Run UI element extraction script")
print()
