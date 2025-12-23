import re
from collections import defaultdict
from typing import List, Generator, Tuple, Optional


class ContentBlock:
    def __init__(self, content: str, block_type: str, level: int = 0,header_stack = None):
        self.content = content
        self.type = block_type  # 'markdown', 'code', 'comment', 'header'
        self.level = level
        self.header_stack = header_stack or []
    def __repr__(self):
        return f"Block('{self.type}', level={self.level}, header_stack={self.header_stack}, content='{self.content[:20].replace('\n','\\n')}...')"

def process_md_blocks(blocks: List[ContentBlock], max_level: int = 1) -> List[ContentBlock]:
    """Обрабатывает markdown блоки: находит заголовки и обновляет уровни"""
    processed_blocks = []
    current_level = 0 
    current_stack = [] 
    for block in blocks:
        #print("Processing block:", block)
        block.level = current_level
        block.header_stack = current_stack.copy()

        if block.type != 'markdown':
            processed_blocks.append(block)
            continue

        lines = block.content.split('\n')
        processed_lines = []
        
        for line in lines:
            # Проверяем, является ли строка заголовком
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                new_level = max(len(header_match.group(1)),1)-1
                last_stack = current_stack.copy()
                if(new_level > 0 and new_level <=max_level):
                    
                    new_block = ContentBlock('\n'.join(processed_lines), 'markdown', current_level,current_stack.copy())
                    #print(f"appbend block {new_block}")
                    processed_lines.clear()

                    processed_blocks.append(new_block)

                    if(new_level > current_level):
                        current_stack.append(1)
                    elif(new_level == current_level):
                        current_stack[-1] += 1
                    else:
                        current_stack = current_stack[:new_level]
                        current_stack[-1] += 1
                    current_level = new_level
                #print(f"Found header: '{line}' with level {new_level}, current_level={current_level},stack = {last_stack}, new_stack={current_stack}")
                processed_lines.append(line)

            else:
                processed_lines.append(line)

        processed_content = '\n'.join(processed_lines)
        #print("appbend block with stack =", current_stack)
        new_block = ContentBlock(processed_content, 'markdown', current_level,current_stack.copy())
        processed_blocks.append(new_block)
    return processed_blocks

def split_blocks(content):
    """Разделяет контент на блоки: код, комментарии, markdown"""
    blocks = []
    i = 0
    n = len(content)
    state = 'markdown'  # 'markdown', 'code', 'comment'
    current_block_start = 0
    
    while i < n:
        if state == 'markdown':
            # Ищем начало кода или комментария
            code_start = content.find('```', i)
            comment_start = content.find('<!--', i)
            
            # Находим ближайший старт
            starts = [(code_start, 'code'), (comment_start, 'comment')]
            starts = [(pos, stype) for pos, stype in starts if pos != -1]
            
            if not starts:
                # Остаток - markdown
                if i < n:
                    blocks.append(ContentBlock(content[i:], 'markdown'))
                break
            
            # Ближайший старт
            next_start, next_type = min(starts, key=lambda x: x[0])
            
            # Добавляем markdown до старта
            if next_start > i:
                blocks.append(ContentBlock(content[i:next_start], 'markdown'))
            
            # Переходим в новое состояние
            state = next_type
            i = next_start
            current_block_start = i
            
            if next_type == 'code':
                i += 3  # Пропускаем ```
            else:  # comment
                i += 4  # Пропускаем <!--
        
        elif state == 'code':
            # Ищем конец блока кода ```
            code_end = content.find('```', i)
            if code_end == -1:
                # Незакрытый блок кода - считаем до конца
                blocks.append(ContentBlock(content[current_block_start:], 'code'))
                break
            
            # Добавляем блок кода
            code_content = content[current_block_start:code_end + 3]
            blocks.append(ContentBlock(code_content, 'code'))
            
            i = code_end + 3
            state = 'markdown'
            current_block_start = i
        
        elif state == 'comment':
            # Ищем конец комментария -->
            comment_end = content.find('-->', i)
            if comment_end == -1:
                # Незакрытый комментарий - считаем до конца
                blocks.append(ContentBlock(content[current_block_start:], 'comment'))
                break
            
            # Добавляем блок комментария
            comment_content = content[current_block_start:comment_end + 3]
            blocks.append(ContentBlock(comment_content, 'comment'))
            
            i = comment_end + 3
            state = 'markdown'
            current_block_start = i
    
    return blocks