#!/usr/bin/env python3
"""
Botrix Agentic Tutorial Assistant - Local CLI Runner
Autonomous multimodal agent creating kid-friendly electronics tutorial packages.
"""

import sys
import os
from pathlib import Path
import argparse
import time

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure src is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import Config
from src.agents.orchestrator import orchestrator
from src.models import JobStatus, JobState


def print_banner():
    print("""
========================================================================
             * BOTRIX AGENTIC TUTORIAL ASSISTANT *
         Taskmaster Track - All Things Agentic Hackathon
========================================================================
""")


def display_job_preview(job: JobState):
    print("\n" + "=" * 70)
    print(">> TUTORIAL PACKAGE PREVIEW <<")
    print("=" * 70)
    if job.script:
        print(f"Video Title: {job.script.title}")
        print(f"Target Audience: {job.script.target_age_group}")
        print(f"Concept: {job.script.explanation_summary}\n")
        
        print("Hardware Components:")
        for c in job.script.components:
            print(f"  * {c.name}: {c.kid_description}")
        print()

    print("Key Moments & Reaction Beats:")
    for km in job.key_moments:
        st = next((s for s in job.stickers if s.moment_id == km.id), None)
        au = next((a for a in job.audio_effects if a.moment_id == km.id), None)
        sticker_file = Path(st.local_path).name if st else "Generating..."
        audio_file = Path(au.local_path).name if au else "Generating..."
        print(f"  [{km.timestamp_str}] Moment {km.id}: {km.moment_title}")
        print(f"     Action:   {km.description}")
        print(f"     Sticker:  {sticker_file} ({km.reaction_prompt[:45]}...)")
        print(f"     SFX:      {audio_file} (Cue: '{km.sfx_query}')")
        print()

    if job.script and job.script.script_lines:
        print("Teleprompter Script Snippet (with Inline Cues):")
        for line in job.script.script_lines[:5]:
            dialogue = line.dialogue
            print(f"  [{line.timestamp_str}] {line.speaker}: {dialogue}")
        if len(job.script.script_lines) > 5:
            print(f"  ... (+ {len(job.script.script_lines) - 5} more lines)")

    print("=" * 70)


def main():
    print_banner()

    parser = argparse.ArgumentParser(description="Botrix Agentic Tutorial Assistant CLI")
    parser.add_argument(
        "--media",
        nargs="+",
        default=[],
        help="Path(s) to tutorial photo(s) or video(s)"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="Make this Arduino build super fun, interactive, and educational for kids (8-12yo) with anime-style reaction beats!",
        help="Goal instructions for the tutorial tone and style"
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Automatically approve and export the package without interactive prompt"
    )
    parser.add_argument(
        "--job-id",
        type=str,
        default=None,
        help="Optional custom job ID"
    )

    args = parser.parse_args()

    # If no media provided, look for default sample
    media_paths = args.media
    if not media_paths:
        sample_img = Config.SAMPLE_DATA_DIR / "arduino_radar.jpg"
        if not sample_img.exists():
            print("Creating sample electronics build media fixture...")
            from sample_data.generate_sample import img
            sample_img.parent.mkdir(parents=True, exist_ok=True)
            img.save(sample_img, "JPEG")
        media_paths = [str(sample_img)]

    print(f"Starting Autonomous Pipeline...")
    print(f"   Input Media: {media_paths}")
    print(f"   User Prompt: \"{args.prompt}\"\n")

    # Step 1-4: Execute multi-agent pipeline
    start_time = time.time()
    job = orchestrator.run_pipeline(
        media_paths=media_paths,
        user_prompt=args.prompt,
        job_id=args.job_id
    )

    if job.status == JobStatus.FAILED:
        print(f"\nPipeline failed: {job.error_message}")
        sys.exit(1)

    elapsed = time.time() - start_time
    print(f"\nPipeline generated preview in {elapsed:.1f}s!")

    display_job_preview(job)

    # Step 5: Interactive Approval / Revision Loop
    while True:
        if args.auto_approve:
            choice = "a"
        else:
            print("Director Options:")
            print("  [A] Approve & Export Final Package")
            print("  [R] Request Revision / Give Director Feedback")
            print("  [Q] Quit without saving")
            try:
                choice = input("\nEnter choice [A/r/q]: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                choice = "q"

        if choice in ["a", "approve", ""]:
            print("\nApproving package and exporting all assets...")
            approved_job = orchestrator.approve_job(job.job_id)
            if approved_job and approved_job.output_dir:
                print(f"\nExported successfully to:")
                print(f"   {approved_job.output_dir}\n")
                print("Generated Deliverables:")
                print(f"   - script.json              (Full metadata & timestamped cues)")
                print(f"   - teleprompter_script.md   (Director script with inline cue tags)")
                print(f"   - stickers/                (Original anime reaction PNG stickers)")
                print(f"   - audio/                   (CC-licensed / 44.1kHz sound effects)")
                print(f"   - manifest.json            (Index mapping moments to assets)")
                print(f"   - index.html               (Interactive multimedia player)\n")
            break

        elif choice in ["r", "revise"]:
            try:
                revision_note = input("\nEnter revision feedback for the agent (e.g. 'Add more jokes about bat sonar!'): ").strip()
            except (EOFError, KeyboardInterrupt):
                revision_note = ""
            if not revision_note:
                revision_note = "Make the tone even more energetic and add a radar sweep cue."
            print(f"\nRegenerating with feedback: '{revision_note}'...")
            job = orchestrator.revise_job(job.job_id, revision_note)
            display_job_preview(job)

        elif choice in ["q", "quit"]:
            print("\nExiting without exporting.")
            break


if __name__ == "__main__":
    main()
