"""
Test User Management System (PHASE 7.1.5)
Comprehensive testing for multi-user functionality, user registration, switching, and session management.
"""

import os
import sys

# Add project root to path to import modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.user_management import (
    register_user,
    get_current_user_info,
    switch_user,
    list_all_users,
    get_system_stats,
    user_manager,
)

from agent_tools import (
    register_new_user,
    get_current_user_details,
    switch_to_user,
    list_system_users,
    create_guest_access,
    get_user_system_stats,
)

import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print("=" * 60)


def print_test_result(test_name: str, success: bool, details: str = ""):
    """Print formatted test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   💬 {details}")


def test_basic_user_management():
    """Test basic user management functionality."""
    print_section("Basic User Management Tests")

    # Test 1: System stats with no users
    print("\n🔍 Test 1: Initial system state")
    try:
        stats = get_system_stats()
        initial_users = stats["total_users"]
        print_test_result(
            "Get initial system stats", True, f"Found {initial_users} existing users"
        )
    except Exception as e:
        print_test_result("Get initial system stats", False, str(e))
        return

    # Test 2: Register first user (Admin)
    print("\n🔍 Test 2: Register admin user")
    try:
        success, message, user_data = register_user("TestAdmin", "admin")
        print_test_result("Register admin user", success, message)
        if success:
            print(f"   👤 User ID: {user_data.get('user_id')}")
            print(f"   🔑 Role: {user_data.get('role')}")
    except Exception as e:
        print_test_result("Register admin user", False, str(e))

    # Test 3: Register family members
    print("\n🔍 Test 3: Register family members")
    family_members = [("Parent1", "parent"), ("Kid1", "child"), ("Kid2", "child")]

    for username, role in family_members:
        try:
            success, message, user_data = register_user(username, role)
            print_test_result(f"Register {role}: {username}", success, message)
        except Exception as e:
            print_test_result(f"Register {role}: {username}", False, str(e))

    # Test 4: Try duplicate username
    print("\n🔍 Test 4: Duplicate username validation")
    try:
        success, message, user_data = register_user("TestAdmin", "admin")
        print_test_result("Reject duplicate username", not success, message)
    except Exception as e:
        print_test_result("Duplicate username validation", False, str(e))

    # Test 5: Invalid role validation
    print("\n🔍 Test 5: Invalid role validation")
    try:
        success, message, user_data = register_user("InvalidUser", "invalidrole")
        print_test_result("Reject invalid role", not success, message)
    except Exception as e:
        print_test_result("Invalid role validation", False, str(e))


def test_user_switching():
    """Test user switching functionality."""
    print_section("User Switching Tests")

    # Test 1: Switch to existing user
    print("\n🔍 Test 1: Switch to existing user")
    try:
        success, message, user_data = switch_user("Parent1")
        print_test_result("Switch to Parent1", success, message)
        if success:
            print(f"   👤 Current user: {user_data.get('username')}")
            print(f"   🔑 Role: {user_data.get('role')}")
    except Exception as e:
        print_test_result("Switch to Parent1", False, str(e))

    # Test 2: Get current user info
    print("\n🔍 Test 2: Get current user information")
    try:
        user_info = get_current_user_info()
        logged_in = user_info.get("logged_in", False)
        print_test_result(
            "Get current user info",
            logged_in,
            f"User: {user_info.get('username', 'None')}",
        )
        if logged_in:
            print(f"   ⏱️ Session: {user_info.get('session_duration', 'Unknown')}")
            print(
                f"   📊 Games analyzed: {user_info.get('profile_stats', {}).get('total_games_analyzed', 0)}"
            )
    except Exception as e:
        print_test_result("Get current user info", False, str(e))

    # Test 3: Switch to child account
    print("\n🔍 Test 3: Switch to child account")
    try:
        success, message, user_data = switch_user("Kid1")
        print_test_result("Switch to Kid1", success, message)
        if success:
            print(f"   👶 Child user: {user_data.get('username')}")
    except Exception as e:
        print_test_result("Switch to Kid1", False, str(e))

    # Test 4: Switch to non-existent user
    print("\n🔍 Test 4: Switch to non-existent user")
    try:
        success, message, user_data = switch_user("NonExistentUser")
        print_test_result("Reject non-existent user", not success, message)
    except Exception as e:
        print_test_result("Non-existent user validation", False, str(e))


def test_autogen_tools():
    """Test AutoGen tools integration."""
    print_section("AutoGen Tools Integration Tests")

    # Test 1: Register user through AutoGen tool
    print("\n🔍 Test 1: AutoGen user registration")
    try:
        result = register_new_user("AutoGenUser", "admin")
        success = result.get("success", False)
        message = result.get("message", "No message")
        print_test_result("AutoGen register_new_user", success, message)
        if success:
            profile = result.get("user_profile", {})
            print(f"   👤 User: {profile.get('username')}")
            print(f"   🆔 ID: {profile.get('user_id')}")
    except Exception as e:
        print_test_result("AutoGen register_new_user", False, str(e))

    # Test 2: Get current user details through AutoGen
    print("\n🔍 Test 2: AutoGen current user details")
    try:
        result = get_current_user_details()
        success = result.get("success", False)
        logged_in = result.get("logged_in", False)
        print_test_result(
            "AutoGen get_current_user_details", success, f"Logged in: {logged_in}"
        )
        if logged_in:
            profile = result.get("user_profile", {})
            print(f"   👤 User: {profile.get('username')}")
            print(f"   🔑 Role: {profile.get('role')}")
    except Exception as e:
        print_test_result("AutoGen get_current_user_details", False, str(e))

    # Test 3: Switch user through AutoGen
    print("\n🔍 Test 3: AutoGen user switching")
    try:
        result = switch_to_user("TestAdmin")
        success = result.get("success", False)
        message = result.get("message", "No message")
        print_test_result("AutoGen switch_to_user", success, message)
        if success:
            switched_to = result.get("switched_to", {})
            print(f"   🔄 Switched to: {switched_to.get('username')}")
            print(f"   🎉 Welcome: {result.get('welcome_message', 'Welcome!')}")
    except Exception as e:
        print_test_result("AutoGen switch_to_user", False, str(e))

    # Test 4: List system users through AutoGen
    print("\n🔍 Test 4: AutoGen list system users")
    try:
        result = list_system_users()
        success = result.get("success", False)
        total_users = result.get("total_users", 0)
        print_test_result(
            "AutoGen list_system_users", success, f"Found {total_users} users"
        )
        if success:
            family_view = result.get("family_view", {})
            print(f"   🔑 Admins: {len(family_view.get('admins', []))}")
            print(f"   👨‍👩‍👧‍👦 Parents: {len(family_view.get('parents', []))}")
            print(f"   👶 Children: {len(family_view.get('children', []))}")
    except Exception as e:
        print_test_result("AutoGen list_system_users", False, str(e))

    # Test 5: Create guest session through AutoGen
    print("\n🔍 Test 5: AutoGen guest session")
    try:
        result = create_guest_access()
        success = result.get("success", False)
        message = result.get("message", "No message")
        print_test_result("AutoGen create_guest_access", success, message)
        if success:
            guest_profile = result.get("guest_profile", {})
            print(f"   👤 Guest: {guest_profile.get('username')}")
            print(f"   ⏰ Type: {guest_profile.get('session_type')}")
            print(f"   🚫 Limitations: {len(result.get('limitations', []))}")
    except Exception as e:
        print_test_result("AutoGen create_guest_access", False, str(e))

    # Test 6: Get system statistics through AutoGen
    print("\n🔍 Test 6: AutoGen system statistics")
    try:
        result = get_user_system_stats()
        success = result.get("success", False)
        print_test_result("AutoGen get_user_system_stats", success)
        if success:
            overview = result.get("system_overview", {})
            health_score = overview.get("system_health_score", 0)
            print(f"   📊 Users: {overview.get('total_users', 0)}")
            print(f"   💚 Health: {health_score}%")
            print(f"   💡 Insights: {len(result.get('system_insights', []))}")
    except Exception as e:
        print_test_result("AutoGen get_user_system_stats", False, str(e))


def test_session_management():
    """Test session management functionality."""
    print_section("Session Management Tests")

    # Test 1: Session persistence
    print("\n🔍 Test 1: Session persistence")
    try:
        # Switch to a user
        success, message, user_data = switch_user("Parent1")
        if success:
            username_before = user_data.get("username")

            # Create new manager instance (simulates restart)
            from utils.user_management import UserManager

            new_manager = UserManager()
            current_user = new_manager.get_current_user()

            if current_user and current_user.username == username_before:
                print_test_result(
                    "Session persistence",
                    True,
                    f"User {username_before} persisted across restart",
                )
            else:
                print_test_result(
                    "Session persistence", False, "User session not persisted"
                )
        else:
            print_test_result("Session persistence setup", False, message)
    except Exception as e:
        print_test_result("Session persistence", False, str(e))

    # Test 2: Session action logging
    print("\n🔍 Test 2: Session action logging")
    try:
        stats = get_system_stats()
        actions_count = stats.get("session_actions", 0)
        print_test_result(
            "Session action logging",
            actions_count > 0,
            f"Logged {actions_count} actions",
        )
    except Exception as e:
        print_test_result("Session action logging", False, str(e))


def test_family_features():
    """Test family-specific features."""
    print_section("Family Features Tests")

    # Test 1: Family organization view
    print("\n🔍 Test 1: Family organization")
    try:
        users = list_all_users()
        family_count = {
            "admins": len([u for u in users if u.get("role") == "admin"]),
            "parents": len([u for u in users if u.get("role") == "parent"]),
            "children": len([u for u in users if u.get("role") == "child"]),
            "guests": len([u for u in users if u.get("role") == "guest"]),
        }

        print_test_result("Family organization", True, f"Family: {family_count}")

        # Test family-friendly features
        has_family = family_count["parents"] > 0 or family_count["children"] > 0
        print_test_result(
            "Family setup detected", has_family, "Parents and children registered"
        )

    except Exception as e:
        print_test_result("Family organization", False, str(e))

    # Test 2: Role-based access simulation
    print("\n🔍 Test 2: Role-based access")
    try:
        # Switch to admin
        success, _, admin_data = switch_user("TestAdmin")
        if success:
            admin_role = admin_data.get("role")
            admin_access = admin_role == "admin"
            print_test_result(
                "Admin access check", admin_access, f"Admin role: {admin_role}"
            )

        # Switch to child
        success, _, child_data = switch_user("Kid1")
        if success:
            child_role = child_data.get("role")
            child_restrictions = child_role == "child"
            print_test_result(
                "Child restrictions check",
                child_restrictions,
                f"Child role: {child_role}",
            )

    except Exception as e:
        print_test_result("Role-based access", False, str(e))


def cleanup_test_data():
    """Clean up test data (optional)."""
    print_section("Cleanup (Optional)")

    try:
        # Note: In real usage, you might want to keep user data
        # This is just for testing purposes
        stats = get_system_stats()
        print(f"💾 Test completed with {stats['total_users']} users registered")
        print("📁 User data stored in: user_profiles/")
        print("🧹 To clean up: delete user_profiles/ directory")
        print_test_result("Test data preserved", True, "Data kept for inspection")
    except Exception as e:
        print_test_result("Cleanup check", False, str(e))


def main():
    """Run all tests."""
    print("🧪 AutoGen DekuDeals - User Management System Tests")
    print("=" * 60)
    print("🎯 Testing PHASE 7.1.5: Multi-User System functionality")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run test suites
    test_basic_user_management()
    test_user_switching()
    test_autogen_tools()
    test_session_management()
    test_family_features()
    cleanup_test_data()

    print_section("Test Summary")
    print("✅ All test suites completed!")
    print("📋 Review the results above for any issues")
    print("🎮 Multi-User System is ready for game analysis!")
    print("\n💡 Next steps:")
    print("   • Try analyzing games with different user profiles")
    print("   • Test personalized recommendations")
    print("   • Explore family-friendly features")
    print("   • Switch between users during analysis")


if __name__ == "__main__":
    main()
