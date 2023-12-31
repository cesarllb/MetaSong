import re
from abc import ABC, abstractmethod


class NamingInterface(ABC):

    @abstractmethod
    def handle(name:str):
        ...
    
    @abstractmethod
    def set_next(self, next) -> None:
        ...

class BaseNaming(NamingInterface):
    next: NamingInterface = None
    def __init__(self, substring: list = []) -> None:
        self.substring: list[str] = substring

    def set_next(self, next: NamingInterface) -> None:
        self.next = next

class RemoveExtension(BaseNaming):
    compatible_format = ('mp3', 'm4a', 'flac', 'wav', 'aac', 'ogg')

    def handle(self, name:str) -> str:
        return_name = ''
        splitted = name.split('.')
        if splitted[-1].lower() in self.compatible_format:
            return_name = ''.join(splitted[:-1]).strip()

        if self.next:
            return self.next.handle(return_name)
        elif return_name:
            return return_name.strip()
        else:
            return None

class CompatibleFormat(BaseNaming):
    compatible_format = ('mp3', 'm4a', 'flac', 'wav', 'aac', 'ogg')

    def handle(self, name:str) -> str:
        return_name = ''
        splitted = name.split('.')
        if splitted[-1].lower() in self.compatible_format:
            return_name = name
            
        if self.next and return_name:
            return self.next.handle(return_name)
        elif return_name:
            return return_name
        else:
            return None
    
class RemoveSubstrings(BaseNaming):
    def handle(self, name:str) -> str:
        return_name = ''
        for rem in self.substring:
            if self.substring and rem.lower() in name.lower():
                aux = name.replace(rem.lower(), '')
                return_name = aux
            elif self.substring and rem in name:
                aux = name.replace(rem, '')
                return_name = aux
        return_name = (return_name[0] if return_name else name).strip()
        return self.next.handle(return_name) if self.next else return_name

class BeginsNumber(BaseNaming):
    def handle(self, name:str) -> str:
        return_name = ''
        for i in range(len(name)):
            if not name[i].isdigit() and not name.isdigit():
                return_name = name[i:].strip()
                break
            else:
                return_name = name
        return_name = return_name.strip()
        return self.next.handle(return_name) if self.next else return_name
    
class RemoveSpaceBeforeExtension(BaseNaming):
    def handle(self, name:str) -> str:
        return_name = ''
        splitted = name.split('.')
        if len(splitted) > 1:
            return_name = '.'.join(splitted[:-1]).strip() + '.' + splitted[-1]
        else:
            return_name = name
        return self.next.handle(return_name) if self.next else return_name
    
class RemoveMultiplesSpaces(BaseNaming):
    def handle(self, name:str) -> str:
        return_name = re.sub(r'\s+', ' ', name)
        return self.next.handle(return_name) if self.next else return_name
    
class RemoveBetweenParenthesis(BaseNaming):
    def handle(self, name:str) -> str:
        return_name = self._find_parenthesis(name)
        return_name = return_name.strip()
        return self.next.handle(return_name) if self.next else return_name
    
    def _find_parenthesis(self, return_name, symbols = (('(', ')'), ('[', ']'), ('{', '}'))):
            for s in symbols:
                first = return_name.find(s[0])
                last = return_name.find(s[1])
                if last != -1:
                    while True:
                        if last < len(return_name) - 1:
                            from_last_to_end:str = return_name[last+1:]
                            if from_last_to_end[0] == s[1]:
                                last +=1
                            else:
                                break
                        else:
                            break
                if first != -1 and last != -1:
                    return_name = (return_name[:first].strip() + ' ' + return_name[last+1:].strip()).strip()

            recursive = False
            #check if there is another open parenthesis and go recursive
            recursive = [True for i in range(len(symbols)) if return_name.find(symbols[i][0]) != -1 and return_name.find(symbols[i][1]) != -1]
            return self._find_parenthesis(return_name, symbols) if recursive else return_name
    

class RemoveSymbols(BaseNaming):
    def handle(self, name: str) -> str:
        split = name.split('.')
        if len(split) > 1:
            no_ext = ''
            for s in split[:-1]:
                no_ext += s       
            ext = split[-1]
            aux = re.sub(r"(?<![a-zA-Z'])'|'(?![a-zA-Z])|[^a-zA-Z0-9']+", " ", no_ext)
            return_name = aux.strip() + '.' + ext
        else:
            aux = re.sub(r"(?<![a-zA-Z'])'|'(?![a-zA-Z])|[^a-zA-Z0-9']+", " ", name)
            return_name = aux.strip()
        return self.next.handle(return_name) if self.next else return_name
    
    
def run_chain(name:str, chain: list, substring: list = []) -> str:
    list_chain = []
    for i, ch in enumerate(chain):
        ch_obj = ch(substring)
        list_chain.append(ch_obj)
        if i > 0:
            list_chain[i-1].set_next(ch_obj)

    return list_chain[0].handle(name)