import ast
import os
import sys
from google import genai

def extract_functions(file_path):
    """parse the python file and extract function definitions""" 
    with open(file_path, 'r') as f: 
        source = f.read()
    
    tree = ast.parse(source)
    functions = []

    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef): 
            func_name = node.name
            args = [arg.arg for arg in node.args.args]
            docstring = ast.get_docstring(node) or ""
            source_code = ast.get_source_segment(source, node)
        functions.append({
            'name': func_name,
            'args': args,
            'docstring': docstring,
            'source_code': source_code
        })
    return functions

def generate_tests_for_functions(func_info):
    """Use Gemini to generate pytest tests for a function"""
    client = genai.Client()

    prompt = f"""
    Generate pytest tests for this following Python function.

    funtions name: {func_info['name']}
    Arguments: {func_info['args']} 
    Docstring: {func_info['docstring']} 
    
    Source code: {func_info['source_code']} 

    requirements:
    1. Generate 3-5 meaningful test cases.
    2. Include edge cases (empty cases, None values, etc.)
    3. use descriptive test function names.
    4. Include asserions that actually test the function's behavior.
    5. Do not include any placeholder tests like `assert True` or `assert False`.
    6. Use pytest framework for the tests.
    """ 
    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=prompt
    )
    return response.text

def main():

    changed_files = sys.argv[1:] if len(sys.argv) > 1 else []

    if not changed_files:
        print("No changed Python files provided for Test Generation.")
        return
    
    all_tests = []
    for file_path in changed_files:
        if not file_path.endswith('.py'):
            continue
        if file_path.startswith('tests/'): 
            continue
        
        print(f"Analyzing : {file_path}")
        functions = extract_functions(file_path)

        for func in functions:
            if func['name'].startswith('_'):
                continue

            print(f"Generating tests for function: {func['name']} in {file_path}")
            gen_test = generate_tests_for_functions(func)
            all_tests.append(gen_test)
    
    for test_path in changed_files:
        if test_path.endswith(".py") and test_path.startswith('tests/'):
            print(f"Appending generated tests to: {test_path}")
            
            with open(test_path, 'a', encoding='utf-8') as t:
                t.write("\n\n")
                for test_code in all_tests:
                    t.write(test_code)
                    t.write("\n\n")

    print("Test generation complete.")

if __name__ == "__main__":
    main()
