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
        self.substring: list = substring

    def set_next(self, next: NamingInterface) -> None:
        self.next = next

class CompatibleFormat(BaseNaming):
    compatible_format = ('mp3', 'm4a', 'flac', 'wav', 'aac', 'ogg')
    def handle(self, name:str) -> str:
        return_name = ''
        splitted = name.split('.')
        if splitted[-1].lower() in self.compatible_format:
            return_name = ''.join(splitted[:-1]).strip()

        return self.next.handle(return_name) if self.next and return_name else None
    
class RemoveSubstrings(BaseNaming):
    def handle(self, name:str) -> str:
        return_name = [name.replace(rem, '') 
                for rem in self.substring 
                if self.substring and rem in name]
        return_name = return_name[0] if return_name else name
        return self.next.handle(return_name) if self.next else return_name

class BeginsNumber(BaseNaming):
    def handle(self, name:str) -> str:
        return_name = ''
        for i in range(len(name)):
            if not name[i].isdigit():
                return_name = name[i:].strip()
                break
            else:
                return_name = name
            
        return self.next.handle(return_name) if self.next else return_name
    
class RemoveBetweenParenthesis(BaseNaming):
    def handle(self, name:str) -> str:
        return_name = self._find_parenthesis(name)
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
    def handle(self, name:str) -> str:
        return_name = ''
        if bool(re.search(r'[^\w\s]', name)):
            return_name = re.sub(r'(?<!\w)(?!\s)[^\w\s]+(?<!\s)(?!\w)', '', name).strip()
        else:
            return_name = name

        return self.next.handle(return_name) if self.next else return_name
    
# to_remove: list,
def chain_naming_run(name:str, substring: list = [],
                     chain: tuple = (CompatibleFormat ,RemoveBetweenParenthesis ,RemoveSymbols , BeginsNumber, RemoveSubstrings)) -> str:
    list_chain = []
    for i, ch in enumerate(chain):
        ch_obj = ch(substring)
        list_chain.append(ch_obj)
        if i > 0:
            list_chain[i-1].set_next(ch_obj)

    return list_chain[0].handle(name)