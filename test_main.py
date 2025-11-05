"""
Tests for main.py safety improvements
"""
import time
from main import prune_stale_sessions, student_cups, sessions_seen, last_seen, STALE_TIMEOUT
import main


def test_prune_stale_sessions():
    """Test that prune_stale_sessions removes stale sessions"""
    # Setup: clear all state
    student_cups.clear()
    sessions_seen.clear()
    last_seen.clear()
    
    # Reset throttle to allow immediate pruning
    main.last_prune_time = 0
    
    # Add some sessions
    now = time.time()
    session1 = "test-session-1"
    session2 = "test-session-2"
    session3 = "test-session-3"
    
    # Session 1: recent (should not be pruned)
    last_seen[session1] = now
    student_cups[session1] = "green"
    sessions_seen.add(session1)
    
    # Session 2: stale (should be pruned)
    last_seen[session2] = now - STALE_TIMEOUT - 100  # Older than STALE_TIMEOUT
    student_cups[session2] = "yellow"
    sessions_seen.add(session2)
    
    # Session 3: recent (should not be pruned)
    last_seen[session3] = now - 60  # 1 minute ago
    student_cups[session3] = "red"
    sessions_seen.add(session3)
    
    # Initial state
    assert len(last_seen) == 3
    assert len(student_cups) == 3
    assert len(sessions_seen) == 3
    
    # Run pruning
    prune_stale_sessions()
    
    # Check that only stale session was removed
    assert session1 in last_seen
    assert session2 not in last_seen
    assert session3 in last_seen
    
    assert session1 in student_cups
    assert session2 not in student_cups
    assert session3 in student_cups
    
    assert session1 in sessions_seen
    assert session2 not in sessions_seen
    assert session3 in sessions_seen
    
    # Verify counts
    assert len(last_seen) == 2
    assert len(student_cups) == 2
    assert len(sessions_seen) == 2
    
    print("✓ test_prune_stale_sessions passed")


def test_prune_empty_state():
    """Test that pruning works on empty state"""
    student_cups.clear()
    sessions_seen.clear()
    last_seen.clear()
    
    # Reset throttle to allow immediate pruning
    main.last_prune_time = 0
    
    # Should not crash on empty state
    prune_stale_sessions()
    
    assert len(last_seen) == 0
    assert len(student_cups) == 0
    assert len(sessions_seen) == 0
    
    print("✓ test_prune_empty_state passed")


def test_prune_no_stale_sessions():
    """Test that pruning leaves recent sessions intact"""
    student_cups.clear()
    sessions_seen.clear()
    last_seen.clear()
    
    # Reset throttle to allow immediate pruning
    main.last_prune_time = 0
    
    now = time.time()
    session1 = "test-session-1"
    session2 = "test-session-2"
    
    # Both sessions are recent
    last_seen[session1] = now
    student_cups[session1] = "green"
    sessions_seen.add(session1)
    
    last_seen[session2] = now - 100
    student_cups[session2] = "yellow"
    sessions_seen.add(session2)
    
    # Run pruning
    prune_stale_sessions()
    
    # All sessions should remain
    assert len(last_seen) == 2
    assert len(student_cups) == 2
    assert len(sessions_seen) == 2
    
    print("✓ test_prune_no_stale_sessions passed")


def test_prune_throttling():
    """Test that pruning is throttled to avoid excessive calls"""
    student_cups.clear()
    sessions_seen.clear()
    last_seen.clear()
    
    # Reset throttle
    main.last_prune_time = 0
    
    # Add a stale session
    now = time.time()
    session1 = "test-session-stale"
    last_seen[session1] = now - STALE_TIMEOUT - 100
    student_cups[session1] = "green"
    sessions_seen.add(session1)
    
    # First call should prune
    prune_stale_sessions()
    assert session1 not in last_seen
    
    # Add another stale session
    session2 = "test-session-stale-2"
    last_seen[session2] = now - STALE_TIMEOUT - 100
    student_cups[session2] = "yellow"
    sessions_seen.add(session2)
    
    # Immediate second call should NOT prune (throttled)
    prune_stale_sessions()
    assert session2 in last_seen  # Still there due to throttling
    
    # Simulate time passing (5+ minutes)
    main.last_prune_time = now - 301
    
    # Now it should prune
    prune_stale_sessions()
    assert session2 not in last_seen
    
    print("✓ test_prune_throttling passed")


if __name__ == "__main__":
    test_prune_stale_sessions()
    test_prune_empty_state()
    test_prune_no_stale_sessions()
    test_prune_throttling()
    print("\n✅ All tests passed!")
