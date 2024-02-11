from jinja2 import Environment, FileSystemLoader
import yaml
import os

"""
메인 폴더에서 실행한다.

dags/{dag}.py로 생성이 되도록 했기 때문에
이 예제에서는 dynamic_dag 폴더 그대로 생성하도록 함.
"""

file_dir = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(file_dir))
template = env.get_template('templated_dag.jinja2')

for f in os.listdir(file_dir):
    if f.endswith((".yaml", ".yml")):
        with open(f"{file_dir}/{f}", "r") as cf:
            config = yaml.safe_load(cf)
            # with open(f"dags/get_price_{config['dag_id']}.py", "w") as f:
            with open(f"{file_dir}/dynamic_get_price_{config['dag_id']}.py", "w") as f:
                f.write(template.render(config))