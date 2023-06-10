import os
import sys

import yaml
from jinja2 import Environment, FileSystemLoader

JINJA_ENV = Environment(loader=FileSystemLoader("./"), trim_blocks=True, lstrip_blocks=True)


def main():
    toc = yaml.safe_load(open("toc.yaml", "r"))
    os.chdir("docs")
    os.system("mkdir -p ref")
    os.system("rm -rf ref/*")
    data = get_data(toc)
    gen_doc_objects(data)
    gen_doc_index(data)


def get_data(toc):
    sys.path.insert(0, os.path.join(sys.path[0], ".."))
    import komm

    def _get_object_data(obj):
        return {
            "name": obj.__name__,
            "summary": obj.__doc__.split(".")[0].strip() + ".",
            "qualname": f"{obj.__module__}.{obj.__qualname__}",
        }

    def _get_objects_data(objects):
        return [_get_object_data(komm.__dict__[obj_name]) for obj_name in objects]

    data = {}
    for module, element in toc.items():
        if isinstance(element, list):  # module has no submodules
            data[module] = _get_objects_data(element)
        else:  # module has submodules
            data[module] = {submodule: _get_objects_data(objects) for submodule, objects in element.items()}
    return data


def gen_doc_objects(toc):
    template = JINJA_ENV.get_template("templates/ref/object.md.jinja2")

    def _gen_doc_file(obj):
        template.stream(obj=obj).dump(f"ref/{obj['name']}.md")

    for elements in toc.values():
        if isinstance(elements, list):  # module has no submodules
            for obj in elements:
                _gen_doc_file(obj)
        else:  # module has submodules
            for objects in elements.values():
                for obj in objects:
                    _gen_doc_file(obj)


def gen_doc_index(data):
    template = JINJA_ENV.get_template("templates/ref/index.md.jinja2")
    template.stream(data=data).dump("ref/index.md")


if __name__ == "__main__":
    main()