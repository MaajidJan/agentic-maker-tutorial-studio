import os
import io
import re
import logging
import urllib.parse
from pathlib import Path
from typing import List, Optional, Tuple
import httpx
from PIL import Image, ImageDraw, ImageFont, ImageFilter

try:
    from ..config import Config
    from ..models import KeyMoment, StickerAsset
except ImportError:
    from src.config import Config
    from src.models import KeyMoment, StickerAsset

logger = logging.getLogger("sticker_artist_agent")


class StickerArtistAgent:
    """
    Autonomous Real Anime Reaction Sticker Agent.
    Searches the web for real iconic anime character reactions (e.g. Mikasa Ackerman angry,
    Eren in shock, Anya shocked, Luffy laughing victory) and processes them into high-resolution
    die-cut anime reaction stickers with white vinyl borders and emotion labels.
    """

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/png,image/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9"
        }

    def generate_stickers_for_moments(
        self,
        moments: List[KeyMoment],
        output_dir: Path
    ) -> List[StickerAsset]:
        """Fetches and creates dynamic reaction stickers for all key moments in the script."""
        stickers_dir = output_dir / "stickers"
        stickers_dir.mkdir(parents=True, exist_ok=True)

        assets: List[StickerAsset] = []

        for moment in moments:
            char_name = getattr(moment, "character_name", getattr(moment, "anime_character", "Character")) or "Character"
            theme_name = getattr(moment, "theme_or_series", getattr(moment, "anime_series", "Theme")) or "Theme"
            filename = f"moment_{moment.id}_{self._slugify(char_name)}_{self._slugify(moment.moment_title)}.png"
            target_path = stickers_dir / filename
            rel_url = f"stickers/{filename}"

            logger.info(f"Dynamically retrieving reaction sticker for Moment {moment.id}: [{char_name} ({theme_name}) - '{moment.reaction_prompt}']...")

            # 1. Dynamically search and process image
            source_url, success, query_used = self._search_and_create_real_anime_sticker(moment, target_path)

            source_type = "dynamic_agent_search"
            if not success:
                logger.warning(f"Could not fetch web image for '{char_name}'. Generating dynamic badge fallback.")
                self._generate_procedural_anime_sticker(moment, target_path)
                source_type = "procedural"

            asset = StickerAsset(
                moment_id=moment.id,
                filename=filename,
                local_path=str(target_path),
                url_path=rel_url,
                character_name=char_name,
                theme_or_series=theme_name,
                emotion=moment.moment_title,
                prompt_used=moment.reaction_prompt,
                search_query_used=query_used,
                source_url=source_url,
                source_type=source_type,
                format="PNG"
            )
            assets.append(asset)

        return assets

    def _search_and_create_real_anime_sticker(self, moment: KeyMoment, output_path: Path) -> Tuple[Optional[str], bool, str]:
        """
        Dynamically searches image repositories using the LLM agent's formulated query
        and processes the result into a clean die-cut sticker.
        """
        char_name = getattr(moment, "character_name", getattr(moment, "anime_character", "Character"))
        theme_name = getattr(moment, "theme_or_series", getattr(moment, "anime_series", ""))
        agent_query = getattr(moment, "image_search_query", "")
        
        # Build search queries (Agent-formulated query first, then variations)
        search_queries = []
        if agent_query:
            search_queries.append(agent_query)
        if moment.reaction_prompt:
            search_queries.append(f"{char_name} {moment.reaction_prompt}")
        if theme_name:
            search_queries.append(f"{char_name} {theme_name} {moment.moment_title} sticker png")
        search_queries.append(f"{char_name} reaction face transparent png")

        candidate_urls: List[str] = []
        active_query = search_queries[0] if search_queries else char_name

        try:
            with httpx.Client(headers=self.headers, follow_redirects=True, timeout=8.0) as client:
                for query in search_queries:
                    if candidate_urls:
                        break
                    active_query = query
                    q_enc = urllib.parse.quote(query)
                    url = f"https://www.bing.com/images/search?q={q_enc}&qft=+filterui:imagesize-medium&FORM=HDRSC2"
                    
                    try:
                        res = client.get(url)
                        if res.status_code == 200:
                            murls = re.findall(r'murl&quot;:&quot;(http[^&]+)&quot;', res.text)
                            for m in murls:
                                lower_m = m.lower()
                                if not any(bad in lower_m for bad in ["bing.com", "microsoft.com", "favicon", "icon", "logo"]):
                                    candidate_urls.append(m)
                                    if len(candidate_urls) >= 8:
                                        break
                    except Exception as e:
                        logger.debug(f"Search query '{query}' error: {e}")

                # Download and process first valid image
                for img_url in candidate_urls:
                    try:
                        img_res = client.get(img_url, timeout=5.0)
                        if img_res.status_code == 200 and len(img_res.content) > 4000:
                            processed = self._process_image_to_sticker(img_res.content, moment, output_path)
                            if processed:
                                logger.info(f"Successfully downloaded and crafted dynamic reaction sticker ({char_name}) from {img_url[:60]}...")
                                return img_url, True, active_query
                    except Exception as e:
                        logger.debug(f"Failed to process image from {img_url[:50]}: {e}")
                        continue

        except Exception as e:
            logger.warning(f"Dynamic sticker search failed: {e}")

        return None, False, active_query

    def _process_image_to_sticker(self, img_bytes: bytes, moment: KeyMoment, output_path: Path) -> bool:
        """Transforms raw anime image bytes into a stylized, die-cut 512x512 PNG reaction sticker."""
        try:
            raw_img = Image.open(io.BytesIO(img_bytes))
            raw_img = raw_img.convert("RGBA")

            size = 512
            canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))

            # Resize to fit within 440x440
            raw_img.thumbnail((430, 430), Image.Resampling.LANCZOS)
            w, h = raw_img.size

            # Check if image has transparency or is a solid photo/frame
            has_alpha = False
            alpha_extrema = raw_img.split()[-1].getextrema()
            if alpha_extrema and alpha_extrema[0] < 200:
                has_alpha = True

            offset_x = (size - w) // 2
            offset_y = (size - h) // 2 - 15  # Shift slightly up to make room for bottom banner tag

            if has_alpha:
                # Direct die-cut vinyl border from alpha mask
                alpha = raw_img.split()[-1]
                mask_canvas = Image.new("L", (size, size), 0)
                mask_canvas.paste(alpha, (offset_x, offset_y))
                
                # Expand mask for thick white border
                expanded_mask = mask_canvas.filter(ImageFilter.MaxFilter(15))
                border_img = Image.new("RGBA", (size, size), (255, 255, 255, 255))
                canvas.paste(border_img, (0, 0), expanded_mask)

                # Drop shadow
                shadow_mask = expanded_mask.filter(ImageFilter.GaussianBlur(6))
                shadow_img = Image.new("RGBA", (size, size), (0, 0, 0, 100))
                canvas_with_shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                canvas_with_shadow.paste(shadow_img, (0, 4), shadow_mask)
                canvas_with_shadow.paste(canvas, (0, 0), canvas)
                canvas = canvas_with_shadow

                # Paste character
                canvas.paste(raw_img, (offset_x, offset_y), raw_img)
            else:
                # Solid anime frame / screenshot: Create a stylish rounded card with thick white die-cut border
                card_mask = Image.new("L", (w, h), 0)
                mask_draw = ImageDraw.Draw(card_mask)
                mask_draw.rounded_rectangle([0, 0, w, h], radius=24, fill=255)

                # White outer border
                border_w, border_h = w + 16, h + 16
                border_x = (size - border_w) // 2
                border_y = (size - border_h) // 2 - 15
                
                draw = ImageDraw.Draw(canvas)
                # Outer white die-cut
                draw.rounded_rectangle([border_x, border_y, border_x + border_w, border_y + border_h], radius=28, fill=(255, 255, 255, 255))
                # Paste cropped anime frame
                canvas.paste(raw_img, (offset_x, offset_y), card_mask)

            # Add Character Name & Moment Banner Tag at the bottom
            draw = ImageDraw.Draw(canvas)
            char_name = getattr(moment, "character_name", getattr(moment, "anime_character", "Character")) or "Character"
            banner_text = f"{char_name.upper()} • {moment.moment_title[:20].upper()}"
            
            draw.rounded_rectangle([40, 442, 472, 495], radius=14, fill=(15, 23, 42, 240), outline=(255, 255, 255, 255), width=3)
            
            try:
                font = ImageFont.load_default()
            except Exception:
                font = None
            draw.text((256, 468), banner_text, fill=(255, 255, 255, 255), anchor="mm", font=font)

            canvas.save(output_path, "PNG")
            return True

        except Exception as e:
            logger.error(f"Error processing image to sticker: {e}")
            return False

    def _generate_procedural_anime_sticker(self, moment: KeyMoment, output_path: Path) -> None:
        """Creates a stylized dynamic badge sticker as a reliable offline fallback."""
        size = 512
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 1. Sticker White Die-cut Border
        draw.ellipse([60, 60, 452, 452], fill=(255, 255, 255, 255), outline=(220, 230, 245, 255), width=8)

        # 2. Outer Gradient Badge
        aura_colors = {
            1: (46, 204, 113),  # Green (Boot)
            2: (52, 152, 219),  # Cyan/Blue (Radar)
            3: (231, 76, 60),   # Red/Orange (Alert)
            4: (241, 196, 15),  # Gold/Yellow (Victory)
        }
        badge_color = aura_colors.get(moment.id % 4 + 1, (52, 152, 219))
        draw.ellipse([75, 75, 437, 437], fill=(badge_color[0], badge_color[1], badge_color[2], 230), outline=(255, 255, 255, 255), width=4)

        char_name = getattr(moment, "character_name", getattr(moment, "anime_character", "Character")) or "Character"
        series_name = getattr(moment, "theme_or_series", getattr(moment, "anime_series", "Dynamic Theme")) or "Theme"

        try:
            font = ImageFont.load_default()
        except Exception:
            font = None

        # Draw icon & character text
        draw.text((256, 190), "✨", fill=(255, 255, 255, 255), anchor="mm", font=font)
        draw.text((256, 240), char_name, fill=(255, 255, 255, 255), anchor="mm", font=font)
        draw.text((256, 270), f"({series_name})", fill=(240, 245, 255, 220), anchor="mm", font=font)
        draw.text((256, 310), f"Reaction: {moment.moment_title}", fill=(255, 255, 255, 255), anchor="mm", font=font)

        # Banner tag
        banner_text = f"MOMENT {moment.id}: {moment.moment_title.upper()}"
        draw.rounded_rectangle([70, 440, 442, 490], radius=12, fill=(15, 23, 42, 240), outline=(255, 255, 255, 255), width=4)
        draw.text((256, 465), banner_text[:30], fill=(255, 255, 255, 255), anchor="mm", font=font)

        img.save(output_path, "PNG")
        logger.info(f"Generated procedural anime fallback sticker -> {output_path.name}")

    def _slugify(self, text: str) -> str:
        slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
        return re.sub(r"[-\s]+", "_", slug)[:25]
