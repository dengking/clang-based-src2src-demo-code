from typing import List

import clang.cindex
from jinja2 import Environment, BaseLoader

jinja_env = Environment(loader=BaseLoader)  # jinja environment
index = clang.cindex.Index.create()  # 创建编译器对象


class StructModel:
    def __init__(self):
        self.from_name = ''  # 源语言中的名称
        self.to_name = ''  # 目标语言的名称
        self.fields: List[StructFieldModel] = []  # 结构体的字段


class StructFieldModel:
    def __init__(self):
        self.from_name = ''  # 源语言中的名称
        self.to_name = ''  # 目标语言的名称
        self.to_type_name = ''  # 目标语言的类型名称


view_template = jinja_env.from_string("""
export interface {{m.to_name}} {
{% for itor in m.fields %}
{{itor.to_name}} : {{itor.to_type_name}} ,
{% endfor %}
}
    """)  # jinja模板


def map_type(cpp_type_name: str):
    """
    将C++类型映射到JavaScript类型
    :param cpp_type_name:
    :return:
    """
    if cpp_type_name == 'std::string':
        return 'string'
    elif cpp_type_name == 'int':
        return 'integer'
    else:
        raise Exception('暂不支持')


def controller(struct_node: clang.cindex.Cursor, model: StructModel) -> str:
    """

    :param model:
    :param struct_node:
    :return:
    """
    model.from_name = model.to_name = struct_node.spelling
    for field_node in struct_node.get_children():
        field_model = StructFieldModel()
        field_model.from_name = field_model.to_name = field_node.spelling
        field_model.to_type_name = map_type(field_node.type.spelling)
        model.fields.append(field_model)
    return view_template.render(m=model)


cpp_code = """
#include <string>
struct NIM_AuthInfo {
    std::string appKey;
    std::string accid;
    int token;
};
"""  # C++源代码

if __name__ == '__main__':
    translation_unit = index.parse(path='test.cpp', unsaved_files=[('test.cpp', cpp_code)], args=['-std=c++11'])  #
    model = StructModel()
    struct_node = list(translation_unit.cursor.get_children())[-1]
    print(controller(struct_node, model))
