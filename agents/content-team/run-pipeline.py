#!/usr/bin/env python3
"""
DevNook Content Pipeline Orchestrator
Runs the 6-step content creation pipeline.

Usage:
  python run-pipeline.py --steps keyword,planner      # Steps 1-2 (research)
  python run-pipeline.py --steps writer,seo,qa,staging  # Steps 3-6 (writing)
  python run-pipeline.py --steps all                   # Full pipeline
  python run-pipeline.py --steps keyword               # Single step

Environment variables required:
  GEMINI_API_KEY     — for keyword, planner, seo agents (Gemini Flash)
  ANTHROPIC_API_KEY  — for writer (Sonnet), qa (Haiku) agents
"""

import argparse
import sys
import time
from datetime import date
from pathlib import Path

# Add project root to path so agents.utils / agents.skills are importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Also add this directory so sibling agents are importable without package path
THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

from agents.utils import registry

STEPS = ["keyword", "planner", "writer", "seo", "qa", "staging"]


def run_step(step: str) -> dict:
    start = time.time()
    today = date.today().isoformat()

    if step == "keyword":
        import keyword_agent
        result = keyword_agent.run()
    elif step == "planner":
        import planner_agent
        result = planner_agent.run()
    elif step == "writer":
        import writer_agent
        result = writer_agent.run()
    elif step == "seo":
        import seo_optimizer
        result = seo_optimizer.run()
    elif step == "qa":
        import qa_agent
        result = qa_agent.run()
    elif step == "staging":
        import staging
        result = staging.run()
    else:
        raise ValueError(f"Unknown step: {step}. Valid steps: {', '.join(STEPS)}")

    duration = time.time() - start
    registry.log_pipeline_run(
        run_date=today,
        step=step,
        processed=result.get("processed", 0),
        passed=result.get("passed", 0),
        rejected=result.get("rejected", 0),
        duration=duration,
        notes=result.get("notes", ""),
        model_used=result.get("model_used", ""),
        input_tokens=result.get("input_tokens", 0),
        output_tokens=result.get("output_tokens", 0),
        estimated_cost_usd=result.get("estimated_cost_usd", 0.0),
    )
    return result


def main():
    parser = argparse.ArgumentParser(description="DevNook Content Pipeline")
    parser.add_argument(
        "--steps",
        default="all",
        help="Comma-separated steps or 'all'. Steps: keyword,planner,writer,seo,qa,staging",
    )
    args = parser.parse_args()

    steps_to_run = STEPS if args.steps == "all" else [s.strip() for s in args.steps.split(",")]

    # Validate
    invalid = [s for s in steps_to_run if s not in STEPS]
    if invalid:
        print(f"ERROR: Unknown step(s): {invalid}. Valid: {STEPS}")
        sys.exit(1)

    print(f"=== DevNook Pipeline — {date.today()} ===")
    print(f"Running steps: {', '.join(steps_to_run)}\n")

    total_passed = 0
    for step in steps_to_run:
        print(f">> [{step.upper()}]")
        try:
            result = run_step(step)
            passed = result.get("passed", 0)
            total_passed += passed
            print(
                f"  processed={result.get('processed', '?')}  "
                f"passed={passed}  "
                f"rejected={result.get('rejected', '?')}"
            )
            if result.get("model_used"):
                print(
                    f"  model={result['model_used']}  "
                    f"tokens_in={result.get('input_tokens', 0):,}  "
                    f"tokens_out={result.get('output_tokens', 0):,}  "
                    f"cost=${result.get('estimated_cost_usd', 0.0):.4f}"
                )
        except Exception as e:
            print(f"  ERROR: {e}")
            raise
        print()

    print(f"=== Pipeline Complete — {total_passed} items passed ===")


if __name__ == "__main__":
    main()
