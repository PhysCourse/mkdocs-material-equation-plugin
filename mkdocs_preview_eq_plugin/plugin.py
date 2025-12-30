from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from mkdocs.structure.files import File

from pathlib import Path

import re
from collections import defaultdict
from typing import List, Generator, Tuple, Optional

from .mdparser import *

class EquationProcessor:
    def __init__(self,max_level: int = 1,dolog=False):
        self.equation_counter = defaultdict(int)
        self. current_prefix = ""
        self.max_level = max_level
        self.log = dolog

    def process_content(self, content: str) -> str:
        m_blocks = split_blocks(content)
        m_blocks = process_md_blocks(m_blocks, self.max_level)
        m_blocks = self._process_md_blocks(m_blocks)
        return self._assemble_blocks(m_blocks)

    def _process_md_blocks(self,blocks : List[ContentBlock]):
        processed_blocks = []
        for block in blocks:
            if block.type != 'markdown':
                processed_blocks.append(block)
                continue

            content = self._process_latex_environments(block.content,block.header_stack)
            processed_blocks.append(ContentBlock(content, 'markdown', block.level))
        return processed_blocks
    
    def _process_latex_environments(self,content: str,header_stack) -> str:
        """Обрабатывает LaTeX окружения \\begin{...}...\\end{...}"""
        def process_environment(match):
            begin_cmd = match.group(1)
            env_name = match.group(2)
            env_content = match.group(3)
            end_cmd = match.group(4)
            
            # Проверяем, это ли уравнение или подобное
            equation_envs = ['equation','displaymath','align','gather','multiline','eqnarray']
            (not self.log) or print("----------\nenv_name = ", env_name,"content =", repr(env_content))
            if not(True in [ (env_name == env) or (env_name == env+'*') for env in equation_envs]):
                return match.group(0)  # Не обрабатываем
            

            # Ищем label в содержимом окружения
            label_match = re.search(r'\\label\{([^}]+)\}', env_content)
            if not label_match:
                label = None
            else:
                env_content = re.sub(r'\\label\{[^}]+\}\s*', '', env_content)
                label = label_match.group(1)
            
            # Нужно найти отступы r'\n\s*' перед \end{...}
            indent_match = re.search(r'\n(\s*)', env_content)
            if indent_match:
                indent = indent_match.group(1)
            else:
                indent = ''
            # Обрабатываем \tag если есть
            env_content,has_tag,equation_number = self._process_tag_command(env_content, env_name, header_stack,indent)
            if(has_tag):
                if(not label):
                    label = f'eq-{equation_number.replace(".","-")}'
                # Создаем анкоры
                start_anchor = f'{indent}<h6 id="{label}" class="anchor-hidden" headertag = "({{equation_number}})"></h6>\n'
                end_anchor = f'\n{indent}<h6 id="end-eq-{label}" class="anchor-hidden"></h6>'
                #(not self.log) or print("set anchor")
            else:
                start_anchor = ""
                end_anchor = ""
                #(not self.log) or print("anchor not set")
            return f'{start_anchor}{begin_cmd}{env_content}{end_cmd}{end_anchor}'
        
        # Паттерн для поиска LaTeX окружений
        # Поддерживает вложенные окружения до 2 уровней
        pattern = r'(\\begin\{\s*(\w+?\*?)\s*\})(.*?)(\\end\{\2\})'
        return re.sub(pattern, process_environment, content, flags=re.DOTALL)

    def _process_tag_command(self, content: str, env_name: str,header_stack,indent = "") -> Tuple[str,bool]:
        """Обрабатывает команду \\tag в уравнении"""
        
        # Если есть \tag, заменяем его содержимое
        equation_number = None
        has_tag = False
        if '\\tag{' in content:
            tag_regex = r'\\tag\{\s*\*\s*\}'
            if(re.match('.*' + tag_regex + '.*',content.strip())):
                old_content = content
                equation_number = self._generate_equation_number(header_stack)
                content = re.sub(
                    tag_regex,
                    f'\\\\tag{{{equation_number}}}',
                    content
                )
                #(not self.log) or print(f'make sub: "{repr(old_content)}" -> "{repr(content)}"')
            else:
                #(not self.log) or print(f'not make sub: {repr(content)}')
                extract_tag_content = re.search(r'\\tag\{\s*([^}]+)\s*\}', content)
                equation_number = extract_tag_content.group(1) if extract_tag_content else "error-tag"

            has_tag = True
        else:
            # Добавляем \tag в подходящее место
            if not env_name.endswith('*'):
                equation_number = self._generate_equation_number(header_stack)
                # Для equation добавляем после \begin{equation}\n
                begin_pos = content.find('\n')
                if begin_pos != -1:
                    content = f'\n{indent}\\tag{{{equation_number}}} ' + content
                else:
                    content = f'\\tag{{{equation_number}}} ' + content
                has_tag = True
        return (content,has_tag,equation_number)
    def _generate_equation_number(self,header_stack) -> str:
        """Генерирует номер уравнения в формате prefix.h1.h2...index"""
        if not header_stack:
            header_part = ""
        else:
            header_part = '.'.join(map(str, header_stack)) + "."
        
        # Увеличиваем счетчик для текущего уровня заголовков
        level_key = tuple(header_stack)
        print("level_key =", level_key,"counter before =", self.equation_counter[level_key])
        self.equation_counter[level_key] += 1
        eq_index = self.equation_counter[level_key]
        print("counter after =", eq_index)
        # Формируем полный номер
        if self.current_prefix:
            new_tag =  f"{self.current_prefix}.{header_part}{eq_index}"
        else:
            new_tag =  f"{header_part}{eq_index}"
        print("generated tag =", new_tag)
        return new_tag

    def _assemble_blocks(self, blocks: List[ContentBlock]) -> str:
        """Собирает блоки обратно в строку"""
        return ''.join(block.content for block in blocks)
    


class PreviewEqPlugin(BasePlugin):
   
    config_scheme = (
        ("max_level", config_options.Type(int, default=1)),
        ("dolog", config_options.Type(bool, default=False))
    )

    def on_files(self, files, config, **kwargs):
        """
        Добавляем файлы в список файлов MkDocs
        """
        # Добавляем CSS файл
        
        css = Path(__file__).parent / "assets" / "preview_eq_plugin_hidden.css"
        css_file = File(
            path='assets/preview_eq_plugin_hidden.css',
            src_dir=str(css.parent.parent),  # ищем в корне проекта
            dest_dir=config['site_dir'],
            use_directory_urls=False
        )
        if (self.config["dolog"]):
            print(f"MyPlugin: добавление CSS файла {css} в конфигурацию")
        
        files.append(css_file)
        if "extra_css" not in config:
            config["extra_css"] = []

        config["extra_css"].append("assets/preview_eq_plugin_hidden.css")
        
        return files 
    
    def on_pre_build(self, config):
        if (self.config["dolog"]):
            print("MyPlugin: сборка началась")
            print(f"Максимальный уровень: {self.config['max_level']}")

    def on_page_markdown(self, markdown, page, config, files):
        max_level = self.config["max_level"]
        dolog = self.config["dolog"]
        m_processor = EquationProcessor(max_level,dolog)
        try:
            return m_processor.process_content(markdown)
        except Exception as e:
            if(dolog):
                raise e
            print(f"❌ Equation processing error: {e}")
        return markdown
    def on_page_content(self, html, /, *, page, config, files):
        #print(html)
        return html

