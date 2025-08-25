import json
import os
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

# Add the parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class FakeEmbData:
    def __init__(self, vec):
        self.embedding = vec


class FakeEmbeddings:
    def create(self, model, input):
        # return unit vectors
        data = [FakeEmbData([0.0, 1.0, 0.0])] * len(input)
        return SimpleNamespace(data=data)


class FakeChatCompletions:
    def create(self, model, messages, temperature, response_format):
        payload = {
            "title": "Test Pack",
            "hypothesis": "H1",
            "expected_lift": {"level": "medium", "metric": "demo requests"},
            "confidence": "Medium",
            "confidence_justification": ["j1", "j2"],
            "risks": ["r1"],
            "assets_needed": ["LP snippet"],
            "suggested_execution_steps": ["s1", "s2"],
        }
        choice = SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))
        return SimpleNamespace(choices=[choice])


class FakeOpenAI:
    def __init__(self):
        self.embeddings = FakeEmbeddings()
        self.chat = SimpleNamespace(completions=FakeChatCompletions())


def test_generate_pack_for_run():
    """Test the generate_pack_for_run function"""
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
        with patch('rfg.generate_pack.OpenAI', return_value=FakeOpenAI()):
            from rfg.generate_pack import generate_pack_for_run
            
            # Create temporary test data
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                test_data = {
                    "domain": "example.com",
                    "signals": {
                        "headlines_paragraphs": ["Example headline with sufficient words for testing."],
                        "lists": [["item1", "item2"]]
                    },
                    "timestamp": "2024-01-01T00:00:00+00:00"
                }
                json.dump(test_data, f)
                temp_file = f.name
            
            try:
                result = generate_pack_for_run(temp_file)
                
                # Check structure
                assert "pack" in result
                assert "metadata" in result
                
                pack = result["pack"]
                metadata = result["metadata"]
                
                # Check required keys
                required_keys = [
                    "title", "hypothesis", "expected_lift", "confidence",
                    "confidence_justification", "risks", "assets_needed", "suggested_execution_steps"
                ]
                for key in required_keys:
                    assert key in pack
                
                # Check metadata
                assert metadata["domain"] == "example.com"
                assert metadata["model"] == "gpt-4o-mini"
                assert metadata["embed_model"] == "text-embedding-3-small"
                assert "citations" in metadata
                assert len(metadata["citations"]) <= 5
                
            finally:
                os.unlink(temp_file)


def test_collect_snippets():
    """Test snippet collection from signals"""
    from rfg.generate_pack import collect_snippets
    
    test_site = {
        "domain": "test.com",
        "signals": {
            "headlines_paragraphs": [
                "This is a test headline with enough words to pass the filter",
                "Another test headline with sufficient content",
                "Short"  # Should be filtered out
            ],
            "lists": [
                ["item1", "item2", "item3"],
                ["single"]  # Should be filtered out
            ]
        }
    }
    
    domain, snippets = collect_snippets(test_site, k=5)
    
    assert domain == "test.com"
    assert len(snippets) > 0
    assert all(len(snippet.split()) >= 4 for snippet in snippets)


def test_make_embeddings():
    """Test embedding creation"""
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
        with patch('rfg.generate_pack.OpenAI', return_value=FakeOpenAI()):
            from rfg.generate_pack import make_embeddings
            
            client = FakeOpenAI()
            texts = ["test text 1", "test text 2"]
            embeddings = make_embeddings(client, texts)
            
            assert len(embeddings) == 2
            assert all(len(emb) > 0 for emb in embeddings)


def test_build_prompt():
    """Test prompt building"""
    from rfg.generate_pack import build_prompt
    
    # Create a temporary prompt template
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Context snippets:\n{{SNIPPETS}}\nOutput JSON.")
        temp_template = f.name
    
    try:
        retrieved_texts = ["snippet1", "snippet2", "snippet3"]
        prompt = build_prompt(temp_template, retrieved_texts)
        
        assert "snippet1" in prompt
        assert "snippet2" in prompt
        assert "snippet3" in prompt
        assert "{{SNIPPETS}}" not in prompt
        
    finally:
        os.unlink(temp_template)


def test_call_llm_json():
    """Test LLM JSON response parsing"""
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
        with patch('rfg.generate_pack.OpenAI', return_value=FakeOpenAI()):
            from rfg.generate_pack import call_llm_json
            
            client = FakeOpenAI()
            prompt = "Generate a test pack"
            result = call_llm_json(client, "gpt-4o-mini", prompt)
            
            assert isinstance(result, dict)
            assert "title" in result
            assert "hypothesis" in result


def test_save_pack():
    """Test pack saving functionality"""
    from rfg.generate_pack import save_pack
    
    test_pack = {
        "title": "Test Pack",
        "hypothesis": "Test hypothesis",
        "expected_lift": {"level": "medium", "metric": "conversion"},
        "confidence": "Medium",
        "confidence_justification": ["reason1"],
        "risks": ["risk1"],
        "assets_needed": ["asset1"],
        "suggested_execution_steps": ["step1"]
    }
    
    with tempfile.TemporaryDirectory() as temp_dir:
        outfile = save_pack(test_pack, "test.com", temp_dir)
        
        assert os.path.exists(outfile)
        assert outfile.endswith('.json')
        
        # Verify content
        with open(outfile, 'r') as f:
            saved_pack = json.load(f)
        
        assert saved_pack["title"] == "Test Pack"
        assert saved_pack["hypothesis"] == "Test hypothesis"


def test_error_handling():
    """Test error handling in generate_pack_for_run"""
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
        with patch('rfg.generate_pack.OpenAI', return_value=FakeOpenAI()):
            from rfg.generate_pack import generate_pack_for_run
            
            # Test with non-existent file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=True) as f:
                # File will be deleted immediately
                pass
            
            try:
                generate_pack_for_run("non_existent_file.json")
                assert False, "Should have raised an exception"
            except RuntimeError as e:
                assert "not found" in str(e)


if __name__ == "__main__":
    # Run tests
    import pytest
    pytest.main([__file__, "-v"])


