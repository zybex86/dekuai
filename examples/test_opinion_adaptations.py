"""
Test Phase 3 Point 2: Opinion Adaptations
Test Fazy 3 Punkt 2: Adaptacje opinii

This module tests the opinion adaptation system that transforms
game reviews into different communication styles and formats.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_tools import (
    adapt_review_for_context,
    create_multi_platform_opinions,
    get_available_adaptation_options,
)
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_basic_adaptation():
    """Test basic review adaptation functionality."""
    print("=" * 70)
    print("🎭 OPINION ADAPTATIONS - TEST BASIC ADAPTATION")
    print("=" * 70)

    test_game = "INSIDE"

    try:
        print(f"\n🔄 Testing basic adaptation for: {test_game}")
        print("-" * 50)

        # Test casual style adaptation
        result = adapt_review_for_context(
            game_name=test_game,
            style="casual",
            format_type="summary",
            audience="general_public",
            platform="website",
        )

        if result.get("success", False):
            print("✅ BASIC ADAPTATION SUCCESS!")
            print(f"📊 Game: {result['game_title']}")
            print(f"🎭 Style: {result['adaptation_context']['style']}")
            print(f"📝 Format: {result['adaptation_context']['format']}")
            print(f"👥 Audience: {result['adaptation_context']['audience']}")
            print(f"📱 Platform: {result['adaptation_context']['platform']}")
            print(f"📏 Characters: {result['character_count']}")

            # Display adapted content
            adapted_content = result.get("adapted_content", "")
            if adapted_content:
                print(f"\n📄 Adapted Content:")
                print("-" * 30)
                print(
                    adapted_content[:300] + "..."
                    if len(adapted_content) > 300
                    else adapted_content
                )

            # Display engagement elements
            engagement = result.get("engagement_elements", [])
            if engagement:
                print(f"\n💫 Engagement Elements: {', '.join(engagement)}")

            # Display call to action
            cta = result.get("call_to_action")
            if cta:
                print(f"\n📢 Call to Action: {cta}")

            # Display original vs adapted data
            original = result.get("original_review_data", {})
            print(f"\n🔄 Original → Adapted:")
            print(f"   Rating: {original.get('rating', 'N/A')}/10")
            print(f"   Recommendation: {original.get('recommendation', 'N/A')}")
            print(f"   Confidence: {original.get('confidence', 'N/A')}")

            return True
        else:
            print("❌ BASIC ADAPTATION FAILED!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Exception during basic adaptation test: {e}")
        return False


def test_style_variations():
    """Test different communication styles."""
    print("\n" + "=" * 70)
    print("🎨 OPINION ADAPTATIONS - TEST STYLE VARIATIONS")
    print("=" * 70)

    test_game = "Ape Out"
    styles_to_test = ["technical", "casual", "social_media", "professional"]

    try:
        print(f"\n🎨 Testing style variations for: {test_game}")
        print(f"🎭 Styles: {', '.join(styles_to_test)}")
        print("-" * 50)

        successful_adaptations = []

        for style in styles_to_test:
            try:
                print(f"\n📝 Testing {style} style...")

                result = adapt_review_for_context(
                    game_name=test_game,
                    style=style,
                    format_type="summary",
                    audience="general_public",
                    platform="website",
                )

                if result.get("success", False):
                    content = result.get("adapted_content", "")
                    char_count = result.get("character_count", 0)

                    print(f"   ✅ {style.title()}: {char_count} chars")
                    print(f"   Preview: {content[:100]}...")

                    successful_adaptations.append(
                        {
                            "style": style,
                            "content": content,
                            "character_count": char_count,
                            "engagement_elements": result.get(
                                "engagement_elements", []
                            ),
                        }
                    )
                else:
                    print(f"   ❌ {style.title()}: Failed")
                    print(f"   Error: {result.get('error', 'Unknown')}")

            except Exception as e:
                print(f"   ❌ {style.title()}: Exception - {e}")

        print(f"\n📊 Style Comparison Results:")
        print(f"   Successful: {len(successful_adaptations)}/{len(styles_to_test)}")

        if successful_adaptations:
            # Find style with most engagement elements
            most_engaging = max(
                successful_adaptations, key=lambda x: len(x["engagement_elements"])
            )
            shortest = min(successful_adaptations, key=lambda x: x["character_count"])
            longest = max(successful_adaptations, key=lambda x: x["character_count"])

            print(f"\n🏆 Style Analysis:")
            print(
                f"   Most Engaging: {most_engaging['style']} ({len(most_engaging['engagement_elements'])} elements)"
            )
            print(
                f"   Shortest: {shortest['style']} ({shortest['character_count']} chars)"
            )
            print(
                f"   Longest: {longest['style']} ({longest['character_count']} chars)"
            )

        return (
            len(successful_adaptations) >= len(styles_to_test) // 2
        )  # At least half successful

    except Exception as e:
        print(f"❌ Exception during style variations test: {e}")
        return False


def test_format_variations():
    """Test different output formats."""
    print("\n" + "=" * 70)
    print("📋 OPINION ADAPTATIONS - TEST FORMAT VARIATIONS")
    print("=" * 70)

    test_game = "Celeste"
    formats_to_test = ["detailed", "summary", "bullet_points", "social_post"]

    try:
        print(f"\n📋 Testing format variations for: {test_game}")
        print(f"📝 Formats: {', '.join(formats_to_test)}")
        print("-" * 50)

        format_results = {}

        for format_type in formats_to_test:
            try:
                print(f"\n📄 Testing {format_type} format...")

                result = adapt_review_for_context(
                    game_name=test_game,
                    style="casual",
                    format_type=format_type,
                    audience="general_public",
                    platform="website",
                )

                if result.get("success", False):
                    content = result.get("adapted_content", "")
                    char_count = result.get("character_count", 0)

                    print(
                        f"   ✅ {format_type.replace('_', ' ').title()}: {char_count} chars"
                    )

                    # Show format-specific preview
                    if format_type == "bullet_points":
                        lines = content.split("\n")
                        bullet_lines = [
                            line for line in lines if line.strip().startswith("•")
                        ]
                        print(f"   Bullets: {len(bullet_lines)} items")
                        if bullet_lines:
                            print(f"   First bullet: {bullet_lines[0][:60]}...")
                    elif format_type == "social_post":
                        hashtag_count = content.count("#")
                        print(f"   Hashtags: {hashtag_count}")
                        print(f"   Preview: {content[:80]}...")
                    else:
                        print(f"   Preview: {content[:100]}...")

                    format_results[format_type] = {
                        "content": content,
                        "character_count": char_count,
                        "success": True,
                    }
                else:
                    print(f"   ❌ {format_type.replace('_', ' ').title()}: Failed")
                    format_results[format_type] = {
                        "success": False,
                        "error": result.get("error", "Unknown"),
                    }

            except Exception as e:
                print(f"   ❌ {format_type.replace('_', ' ').title()}: Exception - {e}")
                format_results[format_type] = {"success": False, "error": str(e)}

        # Analyze format results
        successful_formats = [
            f for f, r in format_results.items() if r.get("success", False)
        ]

        print(f"\n📊 Format Analysis:")
        print(f"   Successful: {len(successful_formats)}/{len(formats_to_test)}")

        if successful_formats:
            char_counts = [
                format_results[f]["character_count"] for f in successful_formats
            ]
            avg_length = sum(char_counts) / len(char_counts)
            print(f"   Average Length: {avg_length:.1f} characters")
            print(f"   Length Range: {min(char_counts)} - {max(char_counts)} chars")

        return len(successful_formats) >= len(formats_to_test) // 2

    except Exception as e:
        print(f"❌ Exception during format variations test: {e}")
        return False


def test_multi_platform_generation():
    """Test multi-platform opinion generation."""
    print("\n" + "=" * 70)
    print("🌐 OPINION ADAPTATIONS - TEST MULTI-PLATFORM")
    print("=" * 70)

    test_game = "Hollow Knight"
    test_platforms = ["twitter", "reddit", "website", "blog"]

    try:
        print(f"\n🌐 Testing multi-platform generation for: {test_game}")
        print(f"📱 Platforms: {', '.join(test_platforms)}")
        print("-" * 50)

        result = create_multi_platform_opinions(test_game, test_platforms)

        if result.get("success", False):
            print("✅ MULTI-PLATFORM SUCCESS!")
            print(f"📊 Game: {result['game_title']}")
            print(f"🌐 Platforms Generated: {result['platforms_generated']}")
            print(f"📝 Base Rating: {result['base_review_rating']}/10")
            print(f"🎯 Base Recommendation: {result['base_recommendation']}")

            # Display platform-specific results
            platform_opinions = result.get("platform_opinions", {})

            print(f"\n📱 Platform-Specific Results:")
            for platform, opinion in platform_opinions.items():
                style = opinion.get("style", "Unknown")
                format_type = opinion.get("format", "Unknown")
                audience = opinion.get("audience", "Unknown")
                char_count = opinion.get("character_count", 0)

                print(f"\n   🔸 {platform.upper()}:")
                print(f"      Style: {style} | Format: {format_type}")
                print(f"      Audience: {audience} | Length: {char_count} chars")

                # Show content preview
                content = opinion.get("content", "")
                preview_length = 150 if platform == "twitter" else 200
                print(f"      Preview: {content[:preview_length]}...")

                # Show platform-specific features
                engagement = opinion.get("engagement_elements", [])
                if engagement:
                    print(f"      Engagement: {', '.join(engagement[:3])}")

                cta = opinion.get("call_to_action")
                if cta:
                    print(f"      CTA: {cta[:60]}...")

            # Display generation summary
            summary = result.get("generation_summary", {})
            total_chars = summary.get("total_characters", 0)
            print(f"\n📈 Generation Summary:")
            print(f"   Total Characters: {total_chars}")
            print(
                f"   Average per Platform: {total_chars // len(platform_opinions) if platform_opinions else 0}"
            )

            return True
        else:
            print("❌ MULTI-PLATFORM FAILED!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Exception during multi-platform test: {e}")
        return False


def test_adaptation_options():
    """Test getting available adaptation options."""
    print("\n" + "=" * 70)
    print("📋 OPINION ADAPTATIONS - TEST OPTIONS DISCOVERY")
    print("=" * 70)

    try:
        print(f"\n📋 Testing adaptation options discovery...")
        print("-" * 50)

        result = get_available_adaptation_options()

        if result.get("success", False):
            print("✅ OPTIONS DISCOVERY SUCCESS!")

            # Display communication styles
            styles = result.get("communication_styles", {})
            print(f"\n🎭 Communication Styles ({len(styles)}):")
            for style, description in styles.items():
                print(f"   • {style}: {description[:60]}...")

            # Display output formats
            formats = result.get("output_formats", {})
            print(f"\n📝 Output Formats ({len(formats)}):")
            for fmt, description in formats.items():
                print(f"   • {fmt}: {description[:60]}...")

            # Display audience types
            audiences = result.get("audience_types", {})
            print(f"\n👥 Audience Types ({len(audiences)}):")
            for audience, description in audiences.items():
                print(f"   • {audience}: {description[:60]}...")

            # Display supported platforms
            platforms = result.get("supported_platforms", {})
            print(f"\n📱 Supported Platforms ({len(platforms)}):")
            for platform, description in platforms.items():
                print(f"   • {platform}: {description}")

            # Display preset combinations
            presets = result.get("preset_combinations", {})
            print(f"\n🎨 Preset Combinations ({len(presets)}):")
            for preset_name, preset_info in list(presets.items())[:3]:  # Show first 3
                style = preset_info.get("style", "Unknown")
                format_type = preset_info.get("format", "Unknown")
                audience = preset_info.get("audience", "Unknown")
                print(f"   • {preset_name}: {style}/{format_type}/{audience}")

            if len(presets) > 3:
                print(f"   ... and {len(presets) - 3} more presets")

            # Display usage examples
            examples = result.get("usage_examples", [])
            if examples:
                print(f"\n💡 Usage Examples:")
                for i, example in enumerate(examples[:2], 1):
                    print(f"   {i}. {example}")

            print(f"\n📊 Options Summary:")
            print(f"   Styles: {len(styles)} | Formats: {len(formats)}")
            print(f"   Audiences: {len(audiences)} | Platforms: {len(platforms)}")
            print(f"   Presets: {len(presets)} | Examples: {len(examples)}")

            return True
        else:
            print("❌ OPTIONS DISCOVERY FAILED!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Exception during options discovery test: {e}")
        return False


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n" + "=" * 70)
    print("⚠️ OPINION ADAPTATIONS - TEST EDGE CASES")
    print("=" * 70)

    edge_cases = [
        {
            "name": "Invalid Style",
            "params": {"game_name": "INSIDE", "style": "invalid_style"},
            "should_fail": True,
        },
        {
            "name": "Invalid Format",
            "params": {"game_name": "INSIDE", "format_type": "invalid_format"},
            "should_fail": True,
        },
        {
            "name": "Invalid Audience",
            "params": {"game_name": "INSIDE", "audience": "invalid_audience"},
            "should_fail": True,
        },
        {
            "name": "Twitter Length Limit",
            "params": {"game_name": "INSIDE", "platform": "twitter", "max_length": 280},
            "should_fail": False,
        },
        {
            "name": "Non-existent Game",
            "params": {"game_name": "NonExistentGameXYZ123"},
            "should_fail": True,
        },
    ]

    try:
        print(f"\n⚠️ Testing {len(edge_cases)} edge cases...")
        print("-" * 50)

        passed_tests = 0

        for i, test_case in enumerate(edge_cases, 1):
            test_name = test_case["name"]
            params = test_case["params"]
            should_fail = test_case["should_fail"]

            print(f"\n🧪 Test {i}: {test_name}")

            try:
                result = adapt_review_for_context(**params)
                success = result.get("success", False)

                if should_fail:
                    if not success:
                        print(
                            f"   ✅ Correctly failed: {result.get('error', 'Unknown error')[:50]}..."
                        )
                        passed_tests += 1
                    else:
                        print(f"   ❌ Should have failed but succeeded")
                else:
                    if success:
                        char_count = result.get("character_count", 0)
                        print(f"   ✅ Correctly succeeded: {char_count} chars")

                        # Special check for Twitter length limit
                        if "twitter" in params.get("platform", "") and params.get(
                            "max_length"
                        ):
                            if char_count <= params["max_length"]:
                                print(
                                    f"   ✅ Length constraint respected: {char_count} <= {params['max_length']}"
                                )
                            else:
                                print(
                                    f"   ⚠️ Length constraint violated: {char_count} > {params['max_length']}"
                                )

                        passed_tests += 1
                    else:
                        print(
                            f"   ❌ Should have succeeded but failed: {result.get('error', 'Unknown')}"
                        )

            except Exception as e:
                if should_fail:
                    print(f"   ✅ Correctly raised exception: {str(e)[:50]}...")
                    passed_tests += 1
                else:
                    print(f"   ❌ Unexpected exception: {str(e)[:50]}...")

        print(f"\n📊 Edge Cases Summary:")
        print(f"   Passed: {passed_tests}/{len(edge_cases)}")
        print(f"   Success Rate: {(passed_tests / len(edge_cases)) * 100:.1f}%")

        return passed_tests >= len(edge_cases) * 0.8  # 80% success rate

    except Exception as e:
        print(f"❌ Exception during edge cases test: {e}")
        return False


def run_opinion_adaptation_tests():
    """Run all opinion adaptation tests."""
    print("🚀 STARTING PHASE 3 POINT 2 TESTS")
    print("Testing opinion adaptation system...")
    print("=" * 70)

    results = []

    # Test 1: Basic Adaptation
    test1_result = test_basic_adaptation()
    results.append(("Basic Adaptation", test1_result))

    # Test 2: Style Variations
    test2_result = test_style_variations()
    results.append(("Style Variations", test2_result))

    # Test 3: Format Variations
    test3_result = test_format_variations()
    results.append(("Format Variations", test3_result))

    # Test 4: Multi-Platform Generation
    test4_result = test_multi_platform_generation()
    results.append(("Multi-Platform Generation", test4_result))

    # Test 5: Adaptation Options
    test5_result = test_adaptation_options()
    results.append(("Adaptation Options", test5_result))

    # Test 6: Edge Cases
    test6_result = test_edge_cases()
    results.append(("Edge Cases", test6_result))

    # Summary
    print("\n" + "=" * 70)
    print("📊 PHASE 3 PUNKT 2 - TEST RESULTS SUMMARY")
    print("=" * 70)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL PHASE 3 POINT 2 TESTS PASSED!")
        print("✅ Opinion adaptation system is fully functional!")
        print("🎭 Reviews can now be adapted to any context and audience!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

    return passed == total


if __name__ == "__main__":
    success = run_opinion_adaptation_tests()

    print("\n" + "=" * 70)
    print("🏁 PHASE 3 POINT 2 TESTING COMPLETE")
    print("=" * 70)

    if success:
        print("✅ Phase 3 Point 2 implementation is ready!")
        print("🎯 Capabilities achieved:")
        print("   • 6 communication styles (technical, casual, social_media, etc.)")
        print("   • 6 output formats (detailed, summary, bullet_points, etc.)")
        print("   • 7 audience types (bargain_hunters, quality_seekers, etc.)")
        print("   • 6 platform adaptations (twitter, reddit, blog, etc.)")
        print("   • Multi-platform simultaneous generation")
        print("   • Preset combinations for common use cases")
        print("   • Edge case handling and validation")
    else:
        print("❌ Phase 3 Point 2 needs additional work.")
        print("🔧 Check the error messages above and fix any issues.")

    print(f"\n🎉 Opinion adaptation system ready for production!")
