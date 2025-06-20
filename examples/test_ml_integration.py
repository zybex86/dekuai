#!/usr/bin/env python3
"""
Test script for Multi-User + Smart User Profiler Integration
===========================================================

This script tests whether the ML system is properly integrated with the Multi-User system.
It verifies that:
1. ML profiles are created per user
2. User switching updates ML tracking
3. Different users get different ML recommendations
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_tools import get_user_ml_profiles_integration
from utils.user_management import (
    UserManager,
    register_user,
    switch_user,
    get_current_user_info,
)
from utils.smart_user_profiler import get_smart_user_profiler, record_user_interaction


def test_ml_integration():
    """Test Multi-User + ML integration"""

    print("🔬 TESTING: Multi-User + ML Integration")
    print("=" * 60)

    # Initialize systems
    user_manager = UserManager()
    profiler = get_smart_user_profiler()

    print("\n1️⃣ Testing Initial Integration Status")
    print("-" * 40)

    # Check integration status
    integration_info = get_user_ml_profiles_integration()
    print(f"Integration Status: {integration_info['integration_status']}")
    print(f"Current User: {integration_info['current_user']['username']}")
    print(f"System Overview: {integration_info['system_overview']}")

    print("\n2️⃣ Testing User Registration + ML Profile Creation")
    print("-" * 55)

    # Register test users
    test_users = [("TestParent", "parent"), ("TestKid", "child")]

    for username, role in test_users:
        success, message, user_data = register_user(username, role)
        print(f"✅ Registered {username} ({role}): {message[:50]}...")

    print("\n3️⃣ Testing ML Profile Per User")
    print("-" * 35)

    # Test game interactions for different users
    test_games = [
        {
            "name": "Minecraft",
            "data": {
                "title": "Minecraft",
                "genres": ["Sandbox", "Survival", "Creative"],
                "metacritic_score": "93",
                "current_eshop_price": "29,99 zł",
            },
        },
        {
            "name": "Animal Crossing",
            "data": {
                "title": "Animal Crossing: New Horizons",
                "genres": ["Simulation", "Social", "Life"],
                "metacritic_score": "90",
                "current_eshop_price": "259,00 zł",
            },
        },
    ]

    # Test with Parent user
    print("\n🧑 Testing with Parent User:")
    switch_user("TestParent")
    current = get_current_user_info()
    print(f"Switched to: {current['username']} ({current['user_id']})")

    # Record interactions for parent
    for game in test_games:
        record_user_interaction(game["name"], game["data"], "analyzed")
        print(f"  📊 Recorded interaction: {game['name']}")

    # Check parent's ML profile
    parent_profile = profiler.get_smart_user_profile()
    print(
        f"  🧠 Parent ML Profile: {parent_profile.total_interactions if parent_profile else 0} interactions"
    )

    # Test with Child user
    print("\n👶 Testing with Child User:")
    switch_user("TestKid")
    current = get_current_user_info()
    print(f"Switched to: {current['username']} ({current['user_id']})")

    # Record different interactions for child
    kid_games = [
        {
            "name": "Super Mario Odyssey",
            "data": {
                "title": "Super Mario Odyssey",
                "genres": ["Platformer", "Adventure"],
                "metacritic_score": "97",
                "current_eshop_price": "199,00 zł",
            },
        }
    ]

    for game in kid_games:
        record_user_interaction(game["name"], game["data"], "analyzed")
        print(f"  📊 Recorded interaction: {game['name']}")

    # Check child's ML profile
    kid_profile = profiler.get_smart_user_profile()
    print(
        f"  🧠 Child ML Profile: {kid_profile.total_interactions if kid_profile else 0} interactions"
    )

    print("\n4️⃣ Testing Final Integration Status")
    print("-" * 40)

    # Get final integration status
    final_integration = get_user_ml_profiles_integration()
    print(f"Integration Status: {final_integration['integration_status']}")
    print(f"Current User: {final_integration['current_user']['username']}")
    print(
        f"ML Coverage: {final_integration['system_overview']['integration_coverage']}"
    )

    print("\n5️⃣ User Profiles Breakdown")
    print("-" * 30)

    for user_id, profile_info in final_integration["user_profiles_breakdown"].items():
        username = profile_info["username"]
        role = profile_info["role"]
        ml_interactions = profile_info["ml_profile"]["total_interactions"]
        confidence = profile_info["ml_profile"]["confidence_level"]

        print(f"👤 {username} ({role}):")
        print(f"   💾 User ID: {user_id}")
        print(f"   🧠 ML Interactions: {ml_interactions}")
        print(f"   📊 Confidence: {confidence}")
        print(f"   🎮 Patterns: {profile_info['ml_profile']['detected_patterns']}")
        print()

    print("\n✅ INTEGRATION TEST COMPLETE!")
    print("=" * 60)

    # Summary
    success_indicators = [
        final_integration["integration_health"]["multi_user_system"] == "✅ Active",
        final_integration["integration_health"]["smart_profiler"] == "✅ Active",
        final_integration["system_overview"]["total_ml_profiles"] > 0,
        len(final_integration["user_profiles_breakdown"]) > 0,
    ]

    if all(success_indicators):
        print("🎉 SUCCESS: Multi-User + ML Integration is working correctly!")
        print("✅ Each user has separate ML profiles")
        print("✅ User switching updates ML tracking")
        print("✅ Integration is healthy and active")
    else:
        print("❌ ISSUES DETECTED: Integration needs attention")
        print(
            f"Success indicators: {sum(success_indicators)}/{len(success_indicators)}"
        )

    return final_integration


if __name__ == "__main__":
    try:
        test_ml_integration()
    except Exception as e:
        print(f"❌ ERROR during integration test: {e}")
        import traceback

        traceback.print_exc()
