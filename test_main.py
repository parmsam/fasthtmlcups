"""
Tests for main.py safety improvements
"""
import time
from main import prune_stale_sessions, student_cups, sessions_seen, last_seen, STALE_TIMEOUT


def test_prune_stale_sessions():
    """Test that prune_stale_sessions removes stale sessions"""
    # Setup: clear all state
    student_cups.clear()
    sessions_seen.clear()
    last_seen.clear()
    
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


if __name__ == "__main__":
    test_prune_stale_sessions()
    test_prune_empty_state()
    test_prune_no_stale_sessions()
    print("\n✅ All tests passed!")
