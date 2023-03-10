from utils.symbol_table import SymbolTable
from utils.compiler_messages import CompilerMessages
from compiler_levels.lexer.tokens import Tokens
from compiler_levels.lexer.lexer import Lexer
from compiler_levels.parser.grammer import Grammar
from compiler_levels.parser.parser import Parser
from compiler_levels.semantic.type_checker import TypeChecker
from compiler_levels.semantic.preprocess import PreProcess
from compiler_levels.IR_generation.IR_generator import IRGenerator
from compiler_levels.IR_generation.IR_optimizer import IR_optimizer
from compiler_levels.tsvm.run_tsvm import RunTSVM
from utils.show_tree import show_tree
import config
from utils.color_prints import Colorprints


class Compiler(object):
    def __init__(self):
        config.global_symbol_table = SymbolTable(None, "global")
        self.lexer_messages = CompilerMessages()
        self.parser_messages = CompilerMessages()
        self.semantic_messages = CompilerMessages()

        self.tokens = Tokens(self.lexer_messages)
        self.lexer = Lexer(self.tokens)

        self.grammar = Grammar(self.parser_messages)
        self.grammar.lexer = self.lexer.lexer # lexer attribute in lexer object of Lexer class!
        self.parser = Parser(self.grammar)

        self.type_checker = TypeChecker(self.semantic_messages)
        self.preprocess = PreProcess(self.semantic_messages)
        self.compiled_failed = False
        self.iR_generator = IRGenerator() 
        self.iR_optimizer = IR_optimizer()
        self.run_tsvm = RunTSVM()
    


    def compile(self, data, show_syntax_tree=False, print_messages=True):

        #self.lexer.build(data)
        if data.strip() == "":
            Colorprints.print_in_red("There was no code in that file!")
            return
        self.parser.build(data)
        try:
            if show_syntax_tree:
                try:
                    show_tree(config.syntax_tree)
                except:
                    Colorprints.print_in_black("***Couldn't build the syntax tree :(***")
            #lexer errors
            if print_messages:
                if self.lexer_messages.errors == 0 and not self.compiled_failed:
                    Colorprints.print_in_green(f"***Congrats! No lexer errors!***")
                    self.lexer_messages.print_messages()

                elif self.lexer_messages.errors != 0 and not self.compiled_failed:
                    Colorprints.print_in_yellow(f"***{self.lexer_messages.errors} lexer errors detected***")
                    self.lexer_messages.print_messages()
                
                #parser errors
                if self.parser_messages.errors == 0 and not self.compiled_failed:
                    Colorprints.print_in_green(f"***Congrats! No parser errors!***")
                    self.parser_messages.print_messages()

                elif self.parser_messages.errors != 0 and not self.compiled_failed:
                    Colorprints.print_in_yellow(f"***{self.parser_messages.errors} parser errors detected***")
                    self.parser_messages.print_messages()

            #semantic
            self.preprocess.visit(config.ast, None)
            self.type_checker.visit(config.ast, None)
            #semantic errors
            if print_messages:
                if self.semantic_messages.errors == 0 and not self.compiled_failed:
                    Colorprints.print_in_green(f"***Congrats! No semantic errors!***")
                    self.semantic_messages.print_messages()

                elif self.semantic_messages.errors != 0 and not self.compiled_failed:
                    Colorprints.print_in_yellow(f"***{self.semantic_messages.errors} semantic errors detected***")
                    self.semantic_messages.print_messages()

            #IR generartion and Optimization
            if self.lexer_messages.errors == 0 and self.parser_messages.errors == 0 and self.semantic_messages.errors == 0:
                self.iR_generator.visit(config.ast, None)
                
                self.iR_optimizer.delete_mov_to_same_register()
                self.iR_optimizer.delete_empty_lines_from_code()

                f = open(".\generated_IR.out", "w")
                f.write(config.iR_code)
                f.close()


                Colorprints.print_in_lightPurple("***TSLANG Terminal***")
                self.run_tsvm.run()

            else:
                self.compiled_failed = True                
        except:
            self.compiled_failed = True

        if self.compiled_failed:
            Colorprints.print_in_red("!!! Compile failed :( !!!")
