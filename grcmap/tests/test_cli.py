from grcmap.cli import main


def test_frameworks_list_exits_zero():
    assert main(["frameworks-list"]) == 0


def test_validate_exits_zero_on_the_real_example():
    assert main(["validate"]) == 0


def test_gaps_command_exits_zero():
    assert main(["gaps", "--framework", "nist-csf-2.0", "--format", "json"]) == 0


def test_coverage_command_exits_zero_for_a_mapped_control():
    assert main(["coverage", "IAM-01"]) == 0


def test_coverage_command_exits_nonzero_for_an_unmapped_control(capsys):
    exit_code = main(["coverage", "NOT-A-REAL-CONTROL"])
    assert exit_code == 1


def test_report_all_frameworks_exits_zero():
    assert main(["report", "--format", "json"]) == 0
