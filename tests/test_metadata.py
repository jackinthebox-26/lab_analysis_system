from lab_analysis_system.metadata import dict_to_string, list_to_string, add_to_metadata

def test_dict_to_string():
    d = {"key1": "value1", "key2": {"nested_key": 42}}
    result = dict_to_string(d)
    
    assert "key1: value1" in result
    assert "key2:" in result
    assert "    nested_key: 42" in result

def test_list_to_string():
    items = ["file1.txt", "file2.csv"]
    result = list_to_string(items, bullet="*")
    
    assert result == "* file1.txt\n* file2.csv"

def test_add_to_metadata_with_header():
    base = "Initial Data"
    addition = "New Data"
    result = add_to_metadata(base, addition, header="SECTION")
    
    expected = "Initial Data\n-----SECTION-----\nNew Data"
    assert result == expected

def test_add_to_metadata_no_header():
    base = "Initial Data"
    addition = "New Data"
    result = add_to_metadata(base, addition)
    
    assert result == "Initial Data\nNew Data"