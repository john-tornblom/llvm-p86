# encoding: utf-8
# Copyright (C) 2013 John Törnblom
#
# This file is part of LLVM-P86.
#
# LLVM-P86 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LLVM-P86 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LLVM-P86.  If not, see <http://www.gnu.org/licenses/>.

'''
Mutation operators for Pascal-86.
'''

import copy

from . import ast
from . import symtab
from . import report
from . import log


class MutationVisitor(ast.NodeVisitor):

    def __init__(self, name, filename, md5):
        self.report = report.MutationReport(name, filename, md5)

    def default_visit(self, node, arg=None):
        if not node:
            return

        for c in filter(None, node.children):
            child = c.accept(self, arg)
            if child != c:
                node.replace(c, child)

        return node

    def make_mut_cmp(self, m_id, cmp_token):
        '''
        Creates a condition that tests the current mutant id against m_id.
        '''
        id_mut = ast.IdentifierNode("getmutationid")
        acc_mut = ast.VarAccessNode(id_mut)
        acc_mut.type = symtab.SIntType(32)

        var_mut = ast.VarLoadNode(acc_mut)
        var_mut.type = symtab.SIntType(32)

        op_cmp = ast.OpNode(cmp_token)
        val_cm = ast.IntegerNode(m_id)
        val_cm.type = symtab.SIntType(32)

        cond = ast.BinaryOpNode(op_cmp, var_mut, val_cm)
        cond.type = symtab.BoolType()

        return cond

    def make_mut_eq(self, m_id):
        '''
        Creates a condition that will evaluate to true, given that
        m_id is the current mutant.
        '''
        return self.make_mut_cmp(m_id, '=')

    def make_mut_neq(self, m_id):
        '''
        Creates a condition that will evaluate to true, given that
        m_id is NOT the current mutant.
        '''
        return self.make_mut_cmp(m_id, '<>')

    def make_mut_in(self, m_set):
        '''
        Creates a condition that will evaluate to true, given that
        the current mutant is within the set m_set.
        '''
        root = self.make_mut_eq(m_set.pop(0))
        for m_id in m_set:
            cond = self.make_mut_eq(m_id)
            op_or = ast.OpNode("or")
            root = ast.BinaryOpNode(op_or, root, cond)
            root.type = symtab.BoolType()

        return root

    def make_mut_not_in(self, m_set):
        '''
        Creates a condition that will evaluate to true, given that
        the current mutant is NOT within the set m_set.
        '''
        root = self.make_mut_neq(m_set.pop(0))
        for m_id in m_set:
            cond = self.make_mut_neq(m_id)
            op_or = ast.OpNode("and")
            root = ast.BinaryOpNode(op_or, root, cond)
            root.type = symtab.BoolType()

        return root

    def make_mut_eq_cond(self, m_id, cond):
        '''
        Creates a condition that will evaluate to true, given that
        m_id is the current mutant AND cond is true.
        '''
        eq_cond = self.make_mut_eq(m_id)

        op_and = ast.OpNode("and")
        ret = ast.BinaryOpNode(op_and, eq_cond, cond)
        ret.type = symtab.BoolType()

        return ret

    def make_mut_neq_cond(self, m_id, cond):
        '''
        Creates a condition that will evaluate to true, given that
        m_id is NOT the current mutant AND cond is true.
        '''
        eq_cond = self.make_mut_neq(m_id)

        op_and = ast.OpNode("and")
        ret = ast.BinaryOpNode(op_and, eq_cond, cond)
        ret.type = symtab.BoolType()

        return ret

    def make_mut_op_or_cond(self, node, sign, cond=None):
        '''
        Generates a mutant of a node by replacing its operator with
        sign, and joins it to cond with an OR operator.
        '''
        # create mutant
        m_id = self.report.add_mutant(node.op.position, sign)
        if m_id is None:
            log.w('mutation', 'a mutant located in at %s was ignored' %
                              node.op.position)
        else:
            mut_cond = copy.deepcopy(node)
            mut_cond.op.name = sign
            mut_cond = self.make_mut_eq_cond(m_id, mut_cond)

            # Joint mutant with root cond
            if cond:
                op_or = ast.OpNode("or")
                cond = ast.BinaryOpNode(op_or, cond, mut_cond)
                cond.type = symtab.BoolType()
            else:
                cond = mut_cond

        return m_id, cond

    def guard_stmt(self, m_id, stmt, op):
        '''
        Wraps a statement with an if-statement, guarded by a
        condition that tests the current mutant id against m_id.

        The wrapper will transform the statement:
            x := 5;
        into:
            if m_id op 1 then x := 5;
        '''
        if m_id is None:
            log.w('mutation', 'a mutant located in at %s was ignored' %
                              stmt.position)
            return stmt

        val_mut = ast.IntegerNode(m_id)
        val_mut.type = symtab.SIntType(32)

        op_neq = ast.OpNode(op)
        id_mut = ast.IdentifierNode("getmutationid")

        acc_mut = ast.VarAccessNode(id_mut)
        acc_mut.type = symtab.SIntType(32)

        var_mut = ast.VarLoadNode(acc_mut)
        var_mut.type = symtab.SIntType(32)

        cond_cm = ast.BinaryOpNode(op_neq, val_mut, var_mut)
        cond_cm.type = symtab.BoolType()

        return ast.IfNode(cond_cm, stmt)

    def enable_stmt(self, m_id, stmt):
        '''
        Wraps a statement with an if-statement, guarded by a
        condition that tests the current mutant id against m_id.

        The wrapper will transform the statement:
            x := 5;
        into:
            if m_id = 1 then x := 5;
        '''

        mut = self.guard_stmt(m_id, stmt, '=')
        mut.branch_prediction = False
        return mut

    def disable_stmt(self, m_id, stmt):
        '''
        Wraps a statement with an if-statement, guarded by a
        condition that tests the current mutant id against m_id.

        The wrapper will transform the statement:
            x := 5;
        into:
            if m_id <> 1 then x := 5;
        '''

        mut = self.guard_stmt(m_id, stmt, '<>')
        mut.branch_prediction = True
        return mut

    def make_bomb_stmt(self, m_id):
        '''
        Creates a bomb statement that will call on the built-in function
        halt, that will halt the execution of the program
        '''
        arg = ast.IntegerNode(1)
        arg.type = symtab.SIntType(32)
        arg = ast.ArgumentListNode(arg)
        
        fn = ast.IdentifierNode('halt')
        fn = ast.FunctionCallNode(fn, arg)
        fn.type = symtab.FunctionType('P86', 'halt')

        return self.enable_stmt(m_id, fn)

    @staticmethod
    def get_value(operand):
        '''
        Finds the value associated with a tree node, if any
        '''
        assert isinstance(operand, ast.Node)

        if isinstance(operand, ast.TypeConvertNode):
            return MutationVisitor.get_value(operand.child)

        if hasattr(operand, 'value'):
            return operand.value
        elif hasattr(operand.type, 'value'):
            return operand.type.value
        else:
            return None


class SdlMutationVisitor(MutationVisitor):

    def __init__(self, filename, md5):
        name = 'Statement deletion'
        MutationVisitor.__init__(self, name, filename, md5)

    def visit_StatementListNode(self, node, arg=None):
        '''
        Generate mutants by guarding statements. Each statement will generate
        one unique mutant. Some statements contain several child-statements,
        such as if-else constructs, and will also generate a unique mutant,
        where the complete construct is disabled.
        '''
        assert isinstance(node, ast.StatementListNode)

        children = []

        for c in node.children:
            c = c.accept(self)

            m_id = self.report.add_mutant(c.position, '(* NOP *)')
            stmt_guard = self.disable_stmt(m_id, c)
            children.append(stmt_guard)

        node._children = children

        return node


class SCMutationVisitor(MutationVisitor):

    def __init__(self, filename, md5):
        name = 'Statement Coverage'
        MutationVisitor.__init__(self, name, filename, md5)

    def visit_StatementListNode(self, node, arg=None):
        '''
        Generate mutants by injecting bombs before each statement.
        Some statements contain several child-statements, such as
        if-else constructs, and will also generate a unique mutant.
        '''
        assert isinstance(node, ast.StatementListNode)

        children = []

        for c in node.children:
            c = c.accept(self)

            m_id = self.report.add_mutant(c.position, 'halt')
            bomb = self.make_bomb_stmt(m_id)
            bomb.iffalse = c
            children.append(bomb)

        node._children = children

        return node


class BoolMutationVisitor(MutationVisitor):

    def wrap_disable_cond(self, cond):
        '''
        Generates one mutant by replacing a condition with false.
        The original condition is kept and guarded. This is useful
        when mutating loops, so infinite loops can be avoided.
        Conditions made up of constants will not be wrapped (e.g true/false).

        The wrapper will transform the expression:
            x >= 0
        into:
            (m_id <> 1) and (x >= 0)

        with m_id set to one, the wrapper will evaluate to false
        with any other value of m_id, the outcome is determined by x.
        '''
        # Don't mutate constants
        if cond.type.value is not None:
            return cond

        s = "a function call at %s will be omitted, global state might be"\
        " affected"
        if isinstance(cond, ast.FunctionCallNode):
            log.w('mutation', s % cond.position)

        m_id = self.report.add_mutant(cond.position, 'false')
        if m_id is None:
            log.w('mutation', 'a mutant located in at %s was ignored' %
                              cond.position)
            return cond

        false_cond = self.make_mut_neq(m_id)

        op_and = ast.OpNode("and")
        ret = ast.BinaryOpNode(op_and, false_cond, cond)
        ret.type = symtab.BoolType()

        return ret

    def wrap_operand(self, cond):
        '''
        Generates two mutants by replacing a condition with true/false.
        The original condition is kept and guarded. Conditions made up of
        constants will not be wrapped (e.g true/false).

        The wrapper will transform the expression:
            x <= 5
        in to:
            (m_id = 1) or ((m_id <> 2) and (x <= 5))

        with m_id set to one, the wrapper will always evaluate to true.
        with m_id set to two, the  wrapper will always evaluate to false.
        with m_id set to any other value, the original expression will
        determine the outcome.
        '''
        # Don't mutate constants
        if cond.type.value is not None:
            return cond

        s = "a function call at %s will be omitted, global state might be"\
        " affected"
        if isinstance(cond, ast.FunctionCallNode):
            log.w('mutation', s % cond.position)

        m_id = self.report.add_mutant(cond.position, 'true')
        if m_id is None:
            log.w('mutation', 'a mutant located in at %s was ignored' %
                              cond.position)
            return cond

        true_cond = self.make_mut_eq(m_id)

        m_id = self.report.add_mutant(cond.position, 'false')
        if m_id is None:
            log.w('mutation', 'a mutant located in at %s was ignored' %
                              cond.position)
            return cond

        false_cond = self.make_mut_neq(m_id)

        op_or = ast.OpNode("or")
        true_cond = ast.BinaryOpNode(op_or, true_cond, cond)
        true_cond.type = symtab.BoolType()

        op_and = ast.OpNode("and")
        ret = ast.BinaryOpNode(op_and, true_cond, false_cond)
        ret.type = symtab.BoolType()

        return ret


class DCCMutationVisitor(BoolMutationVisitor):

    def __init__(self, filename, md5):
        name = 'Decision/Condition Coverage'
        BoolMutationVisitor.__init__(self, name, filename, md5)

    def visit_UnaryOpNode(self, node, arg=None):
        '''
        Replaces boolean unary operators with true/false
        '''
        assert isinstance(node, ast.UnaryOpNode)

        if (isinstance(node.type, symtab.BoolType) and
            isinstance(node.expr.type, symtab.BoolType)):
            return self.wrap_operand(node)
        else:
            return node

    def visit_CaseListElementNode(self, node, arg):
        '''
        Insert a bomb in cases
        '''
        assert isinstance(node, ast.CaseListElementNode)

        node.case_constant_list = node.case_constant_list.accept(self)

        m_id = self.report.add_mutant(node.statement.position, 'halt')

        bomb = self.make_bomb_stmt(m_id)
        bomb.iffalse = node.statement.accept(self)
        node.statement = bomb

        return node

    def visit_CaseStatementNode(self, node, arg):
        '''
        Insert a bomb in the 'otherwise' branch
        '''
        assert isinstance(node, ast.CaseStatementNode)

        max_num_cases = node.case_index.type.hi - node.case_index.type.lo + 1
        const_values = set()

        for case in node.case_list_element_list.children:
            for const in case.case_constant_list.children:
                val = self.get_value(const)
                if val is not None:
                    const_values.add(val)

        node.case_index = node.case_index.accept(self)
        node.case_list_element_list = node.case_list_element_list.accept(self)

        if node.otherwise:
            node.otherwise = node.otherwise.accept(self)
            m_id = self.report.add_mutant(node.otherwise.position, 'halt')
        elif len(const_values) != max_num_cases:
            pos = copy.deepcopy(node.position)
            pos.lexpos = pos.lexendpos - 3    # insert before the 'end' keyword
            pos.lexendpos = pos.lexpos        # ugly as hell, but it works :P

            #  extra space at the end required
            m_id = self.report.add_mutant(pos, 'otherwise: halt ')
        else:
            m_id = None

        if m_id:
            bomb = self.make_bomb_stmt(m_id)
            bomb.iffalse = node.otherwise
            node.otherwise = bomb

        return node

    def visit_FunctionCallNode(self, node, arg=None):
        '''
        Replaces boolean function calls with arguments with true/false
        '''
        assert isinstance(node, ast.FunctionCallNode)

        if node.arg_list:
            node.arg_list = node.arg_list.accept(self, arg)

        if isinstance(node.type, symtab.BoolType):
            return self.wrap_operand(node)
        else:
            return node

    def visit_ArgumentNode(self, node, arg=None):
        '''
        Replaces boolean function argument with the constants true/false.
        '''
        assert isinstance(node, ast.ArgumentNode)

        if node.expr and isinstance(node.expr.type, symtab.BoolType):
                node.expr = self.wrap_operand(node.expr)

        return node

    def visit_VarLoadNode(self, node, arg=None):
        '''
        Replaces boolean functions without arguments,
        and variables with the constants true/false.
        '''
        assert isinstance(node, ast.VarLoadNode)

        if isinstance(node.type, symtab.BoolType):
            return self.wrap_operand(node)
        else:
            return node

    def visit_BinaryOpNode(self, node, arg=None):
        '''
        Replaces boolean binary operations with true/false
        '''
        assert isinstance(node, ast.BinaryOpNode)

        node.left = node.left.accept(self)
        node.right = node.right.accept(self)

        if isinstance(node.type, symtab.BoolType):
            return self.wrap_operand(node)
        else:
            return node


class StatementMutationVisitor(MutationVisitor):

    def default_visit(self, node, arg):
        l = []
        for c in filter(None, node.children):
            child, muts = c.accept(self, arg)
            if child != c:
                node.replace(c, child)

            l.extend(muts)

        return node, l

    def visit_StatementListNode(self, node, arg):
        '''
        Generate mutants by guarding statements. Each statement will generate
        one unique statement. Some statements contain several child-statements,
        such as if-else constructs, and will also generate a unique mutant.
        '''
        assert isinstance(node, ast.StatementListNode)

        l = []
        for c in filter(None, node.children):
            org, muts = c.accept(self, c)
            prev = None

            for m in muts:
                assert isinstance(m, ast.IfNode)

                if prev:
                    prev.iffalse = m
                else:
                    l.append(m)
                prev = m

            if prev:
                prev.iffalse = org
            else:
                l.append(org)

        node._children = l

        return node, []

    def find_node(self, org, mut):
        if not org or not org.position or not mut.position:
            return None

        if (org.position.lexpos    == mut.position.lexpos and
            org.position.lexendpos == mut.position.lexendpos and
            type(org)              == type(mut)):
                return org

        for c in filter(None, org.children):
            if not c.position:
                continue

            c = self.find_node(c, mut)
            if not c:
                continue

            return c


class AorMutationVisitor(StatementMutationVisitor):

    # div & mod may require extra spaces around them
    # e.g i+5 ---> i mod 5 (only important when rendering
    # the html report).

    _MUTANT = dict()
    _MUTANT['+']   = [     '-', '*', '/', ' div ', ' mod ', 'left', 'right']
    _MUTANT['-']   = ['+',      '*', '/', ' div ', ' mod ', 'left', 'right']
    _MUTANT['*']   = ['+', '-',      '/', ' div ', ' mod ', 'left', 'right']
    _MUTANT['/']   = ['+', '-', '*',      ' div ', ' mod ', 'left', 'right']
    _MUTANT['div'] = ['+', '-', '*', '/',           'mod',  'left', 'right']
    _MUTANT['mod'] = ['+', '-', '*', '/', 'div',            'left', 'right']

    _VALID_COMBO = dict()
    _VALID_COMBO[symtab.IntType] = ['+', '-', '*', 'div', 'mod', ' div ',
                                    ' mod ', 'left', 'right']
    _VALID_COMBO[symtab.RealType] = ['+', '-', '*', '/', 'left', 'right']
    _VALID_COMBO[symtab.SetType] = ['+', '-', '*', 'left', 'right']
    _VALID_COMBO[symtab.EmptySetType] = ['+', '-', '*', 'left', 'right']

    def __init__(self, filename, md5):
        name = 'Arithmetic Operator Replacement'
        StatementMutationVisitor.__init__(self, name, filename, md5)

    def visit_BinaryOpNode(self, node, root):
        assert isinstance(node, ast.BinaryOpNode)

        l = []
        node.left, lm = node.left.accept(self, root)
        node.right, rm = node.right.accept(self, root)

        l.extend(lm)
        l.extend(rm)

        lval = self.get_value(node.left)
        rval = self.get_value(node.right)

        valid_mutants = []
        for Cls in self._VALID_COMBO.keys():
            if isinstance(node.type, Cls):
                valid_mutants.extend(self._VALID_COMBO[Cls])

        if node.op.name in self._MUTANT:
            for op in self._MUTANT[node.op.name]:

                if op not in valid_mutants:
                    continue

                elif op in ['left', 'right']:
                    mut_root = copy.deepcopy(root)
                    mut = self.find_node(mut_root, node)

                    lval = self.get_value(node.left)
                    rval = self.get_value(node.right)

                    if isinstance(node.type, symtab.SetType):
                        val = ast.SetEmptyNode()
                        ty = symtab.EmptySetType()
                    elif isinstance(node.type, symtab.IntType):
                        val = ast.IntegerNode(0)
                        ty = symtab.SIntType(16)
                    elif isinstance(node.type, symtab.RealType):
                        val = ast.RealNode(0.0)
                        ty = symtab.FloatType()
                    else:
                        continue

                    # Disable the left operator
                    if op == 'right':
                        if lval is 0:
                            continue

                        mut.left = val
                        mut.left.type = ty
                        mut.left = ast.TypeConvertNode(mut.left)
                        mut.left.type = mut.right.type

                        pos = copy.deepcopy(node.position)
                        pos.lexendpos = node.op.position.lexendpos

                    # Disable the right operator
                    elif op == 'left':
                        if rval is 0:
                            continue

                        mut.right = val
                        mut.right.type = ty
                        mut.right = ast.TypeConvertNode(mut.right)
                        mut.right.type = mut.left.type

                        pos = copy.deepcopy(node.op.position)
                        pos.lexendpos = node.position.lexendpos

                    # change the operator to +
                    mut = self.find_node(mut_root, node.op)
                    mut.name = '+'

                    m_id = self.report.add_mutant(pos, '(* NOP *)')
                    stmt_guard = self.enable_stmt(m_id, mut_root)

                    l.append(stmt_guard)

                else:
                    mut_root = copy.deepcopy(root)
                    mut = self.find_node(mut_root, node.op)
                    mut.name = op.replace(' ', '')

                    m_id = self.report.add_mutant(mut.position, op)
                    stmt_guard = self.enable_stmt(m_id, mut_root)

                    l.append(stmt_guard)

        return node, l


class CorMutationVisitor(StatementMutationVisitor):

    _MUTANT = dict()
    _MUTANT['and'] = ['=', 'false', 'left', 'right']
    _MUTANT['or'] =  ['<>', 'true', 'left', 'right']

    def __init__(self, filename, md5):
        name = 'Conditional Operator Replacement'
        StatementMutationVisitor.__init__(self, name, filename, md5)

    def visit_BinaryOpNode(self, node, root):
        assert isinstance(node, ast.BinaryOpNode)

        l = []
        node.left, lm = node.left.accept(self, root)
        node.right, rm = node.right.accept(self, root)

        l.extend(lm)
        l.extend(rm)

        if not node.op.name in self._MUTANT:
            return node, l

        for op in self._MUTANT[node.op.name]:
            mut_root = copy.deepcopy(root)

            # replace the expr with either true or false
            if op in ['true', 'false']:
                mut = self.find_node(mut_root, node)

                c = ast.IdentifierNode(op)
                c = ast.VarAccessNode(c)
                c.type = symtab.BoolType()
                c = ast.VarLoadNode(c)
                c.type = symtab.BoolType()

                mut_root.replace(mut, c)

            # replace the expr with either left or right,
            # by setting  left or right to either true or false
            elif op in ['left', 'right']:
                mut = self.find_node(mut_root, getattr(node, op))
                if node.op.name == 'and':
                    op = 'true'
                else:
                    op = 'false'

                c = ast.IdentifierNode(op)
                c = ast.VarAccessNode(c)
                c.type = symtab.BoolType()
                c = ast.VarLoadNode(c)
                c.type = symtab.BoolType()

                mut_root.replace(mut, c)
            else:
                mut = self.find_node(mut_root, node.op)
                mut.name = op

            m_id = self.report.add_mutant(mut.position, op)
            stmt_guard = self.enable_stmt(m_id, mut_root)
            l.append(stmt_guard)

        return node, l


class RorMutationVisitor(StatementMutationVisitor):
    _MUTANT = dict()
    _MUTANT['>'] = ['<=', '<>', 'false']
    _MUTANT['<'] = ['>=', '<>', 'false']
    _MUTANT['<='] = ['<', '=', 'true']
    _MUTANT['>='] = ['>', '=', 'true']
    _MUTANT['='] = ['>=', '<=', 'false']
    _MUTANT['<>'] = ['<', '>', 'true']

    def __init__(self, filename, md5):
        name = 'Relational Operator Replacement'
        StatementMutationVisitor.__init__(self, name, filename, md5)

    def detect_equivalent_mutant(self, node, mut):
        assert isinstance(node, ast.BinaryOpNode)

        lty = node.left.type
        rty = node.right.type

        if not hasattr(lty, 'lo') or not hasattr(lty, 'hi'):
            return False

        if not hasattr(rty, 'lo') or not hasattr(rty, 'hi'):
            return False

        lval = self.get_value(node.left)
        rval = self.get_value(node.right)
        op = node.op.name

        # if b = True   ----> if b >= True
        if op == '=' and mut == '>=' and lty.hi == rval:
            return True

        # if b = False   ----> if b <= False
        if op == '=' and mut == '<=' and lty.lo == rval:
            return True

        # if True = b   ----> if True >= b
        if op == '=' and mut == '>=' and rty.hi == lval:
            return True

        # if False = b   ----> if False <= b
        if op == '=' and mut == '<=' and rty.lo == lval:
            return True

        return False

    def visit_BinaryOpNode(self, node, root):
        assert isinstance(node, ast.BinaryOpNode)

        l = []
        node.left, lm = node.left.accept(self, root)
        node.right, rm = node.right.accept(self, root)

        l.extend(lm)
        l.extend(rm)

        if not isinstance(node.type, symtab.BoolType):
            return node, l

        # Sets not supported
        if isinstance(node.left.type, symtab.SetType):
            return node, l

        if isinstance(node.right.type, symtab.SetType):
            return node, l

        if not node.op.name in self._MUTANT:
            return node, l

        for op in self._MUTANT[node.op.name]:
            if self.detect_equivalent_mutant(node, op):
                continue

            # replace the expr with either true or false
            mut_root = copy.deepcopy(root)
            if op in ['true', 'false']:
                mut = self.find_node(mut_root, node)

                c = ast.IdentifierNode(op)
                c = ast.VarAccessNode(c)
                c.type = symtab.BoolType()
                c = ast.VarLoadNode(c)
                c.type = symtab.BoolType()

                mut_root.replace(mut, c)
            else:
                mut = self.find_node(mut_root, node.op)
                mut.name = op

            m_id = self.report.add_mutant(mut.position, op)
            stmt_guard = self.enable_stmt(m_id, mut_root)

            l.append(stmt_guard)

        return node, l
