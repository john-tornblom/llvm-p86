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
Translate a syntax tree to Pascal-86 source code.
'''

import re
import os

from . import ast


def _trim_line(line, max_length):
    s = str('')

    prefix_len = len(re.match('^[ ]*', line).group(0))
    prefix_len += 6

    length = 0
    for w in line.split(' '):
        if not len(w):
            continue

        if len(w) + length > max_length:
            s += '\n' + (' ' * prefix_len)
            length = prefix_len

        length += len(w)
        s += w + ' '

    return s


def split_long_lines(src, max_length):
    '''
    Inserts newlines at appropriate places so that no line is
    greater than max_length.
    '''
    s = str('')

    for l in src.split('\n'):
        if len(l) <= max_length:
            s += l + '\n'
        else:
            s += _trim_line(l, max_length) + '\n'

    return s


class SourceVisitor(ast.NodeVisitor):

    def __init__(self, filename):
        self.filename = os.path.basename(filename)
        self.scope = 0
        self.current_source = None

    def visit(self, node, arg=None):

        # Probably a mutation, assume its part of the original input file
        if not node.position and self.current_source == self.filename:
            return ast.NodeVisitor.visit(self, node, arg)

        # Original input
        if node.position.path[-1] == self.filename:
            self.current_source = node.position.path[-1]
            return ast.NodeVisitor.visit(self, node, arg)
        else:
            # Included file
            if (node.position.path[-1] != self.current_source and
                node.position.path[-2] == self.filename):
                self.current_source = node.position.path[-1]

                s = '\n$include(%s)\n' % self.current_source

                for c in filter(None, node.children):
                    s += self.visit(c, arg)

                return s

        return ''

    def default_visit(self, node, arg=None):
        string = ''
        for c in filter(None, node.children):
            if not isinstance(c, ast.Node):
                continue

            s = c.accept(self, arg)
            if s is not None:
                string += s

        return string

    def new_line(self):
        string = '\n'
        string += '    ' * self.scope

        return string

    def visit_ProgramNode(self, node, arg=None):
        assert isinstance(node, ast.ProgramNode)

        name = node.identifier.accept(self)
        if node.identifier_list:
            args = '(' + node.identifier_list.accept(self) + ')'
        else:
            args = ''

        string = 'PROGRAM %s%s;' % (name, args)
        string += self.new_line()

        if node.block:
            string += node.block.accept(self)

        string += self.new_line()
        string += '. (* PROGRAM *)' + self.new_line()

        return re.sub(r'\n[ ]*\n', '\n', string)

    def visit_ModuleNode(self, node, arg=None):
        assert isinstance(node, ast.ModuleNode)

        string = 'MODULE %s;' % node.identifier.accept(self)
        string += self.new_line()

        if node.interface:
            string += node.interface.accept(self)
            string += self.new_line()

        if node.entry_point:
            string += node.entry_point.accept(self)
            string += self.new_line()

        return re.sub(r'\n[ ]+\n', '\n', string)

    def visit_PublicSectionNode(self, node, arg=None):
        assert isinstance(node, ast.PublicSectionNode)

        string = 'PUBLIC %s;' % node.identifier.accept(self)
        self.scope += 1
        string += self.new_line()

        string += node.section.accept(self)

        self.scope -= 1
        string += self.new_line()

        return string

    def visit_NonMainNode(self, node, arg=None):
        assert isinstance(node, ast.NonMainNode)

        string = 'PRIVATE %s;' % node.identifier.accept(self)
        self.scope += 1
        string += self.new_line()

        if node.const_list:
            string += node.const_list.accept(self)

        if node.type_list:
            string += node.type_list.accept(self)

        if node.var_list:
            string += node.var_list.accept(self)

        if node.func:
            string += node.func.accept(self)

        self.scope -= 1
        string += self.new_line()
        string += '. (* PRIVATE *)' + self.new_line()

        return string

    def visit_SectionNode(self, node, arg=None):
        assert isinstance(node, ast.SectionNode)

        string = ''
        prefix = ''
        for c in node.children:
            if c is None:
                string += prefix
                prefix = ''
            else:
                string += c.accept(self, arg)
                prefix = self.new_line()

        return string

    def visit_PublicFunctionNode(self, node, external):
        assert isinstance(node, ast.PublicFunctionNode)

        string = self.new_line()
        string += 'FUNCTION %s;' % node.heading.accept(self)

        return string

    def visit_PublicProcedureNode(self, node, external):
        assert isinstance(node, ast.PublicProcedureNode)

        string = self.new_line()
        string += 'PROCEDURE %s;' % node.heading.accept(self)

        return string

    def visit_FunctionNode(self, node, arg=None):
        assert isinstance(node, ast.FunctionNode)

        string = self.new_line()
        if node.attr:
            string += '(*.' + node.attr.accept(self) + '.*) '
        string += 'FUNCTION %s;' % node.header.accept(self)
        self.scope += 1
        string += self.new_line()
        string += node.block.accept(self)
        string += ';'
        self.scope -= 1
        string += self.new_line()

        return string

    def visit_ProcedureNode(self, node, arg=None):
        assert isinstance(node, ast.ProcedureNode)

        string = self.new_line()
        if node.attr:
            string += '(*.' + node.attr.accept(self) + '.*) '
        string += 'PROCEDURE %s;' % node.header.accept(self)
        self.scope += 1
        string += self.new_line()
        string += node.block.accept(self)
        string += ';'
        self.scope -= 1
        string += self.new_line()

        return string

    def visit_BlockNode(self, node, arg=None):
        assert isinstance(node, ast.BlockNode)

        string = ''
        if node.label_list:
            string += node.label_list.accept(self)

        if node.const_list:
            string += node.const_list.accept(self)

        if node.type_list:
            string += node.type_list.accept(self)

        if node.var_list:
            string += node.var_list.accept(self)

        if node.func:
            string += node.func.accept(self)

        if node.stmt:
            string += self.new_line() + 'BEGIN'

            self.scope += 1
            string += self.new_line()
            string += node.stmt.accept(self)
            self.scope -= 1

            string += self.new_line() + 'END'

        return string

    def visit_WithNode(self, node, arg=None):
        assert isinstance(node, ast.WithNode)

        records = node.rec_var_list.accept(self)

        string = 'WITH %s DO BEGIN' % records

        self.scope += 1
        string += self.new_line()
        string += node.statement_list.accept(self)
        self.scope -= 1

        string += self.new_line() + 'END (* WITH *)'

        return string

    def visit_IndexedVarNode(self, node, field=None):
        assert isinstance(node, ast.IndexedVarNode)

        string = node.var_access.accept(self)

        for c in node.index_expr_list.children:
            string += '[%s]' % c.accept(self)

        return string

    def visit_VarAccessNode(self, node, field):
        assert isinstance(node, ast.VarAccessNode)

        return node.identifier.accept(self)

    def visit_FieldAccessNode(self, node, field=None):
        assert isinstance(node, ast.FieldAccessNode)

        field = node.identifier.accept(self)
        var = node.var_access.accept(self)

        return var + '.' + field

    def visit_PointerAccessNode(self, node, field):
        assert isinstance(node, ast.PointerAccessNode)

        string = node.var_access.accept(self)

        return string + '^'

    def visit_UnaryOpNode(self, node, arg=None):
        assert isinstance(node, ast.UnaryOpNode)

        op = node.name
        expr = node.expr.accept(self)

        if op == 'not':
            return '%s %s' % (op, expr)
        else:
            return '%s%s' % (op, expr)

    def visit_BinaryOpNode(self, node, arg=None):
        assert isinstance(node, ast.BinaryOpNode)

        sign = node.op.name

        left = node.left.accept(self)
        right = node.right.accept(self)

        return '((%s) %s (%s))' % (left, sign, right)

    def visit_IfNode(self, node, arg=None):
        assert isinstance(node, ast.IfNode)

        expr = node.expr.accept(self)

        string = 'IF %s THEN BEGIN' % expr
        self.scope += 1
        string += self.new_line()

        if node.iftrue:
            string += node.iftrue.accept(self)
        else:
            string += '(* NOP *)'

        self.scope -= 1
        string += self.new_line()
        string += 'END'

        if node.iffalse:
            string += self.new_line()
            string += 'ELSE BEGIN'
            self.scope += 1
            string += self.new_line()
            string += node.iffalse.accept(self)
            self.scope -= 1

            string += self.new_line()
            string += 'END'

        return string

    def visit_WhileNode(self, node, arg=None):
        assert isinstance(node, ast.WhileNode)

        cond = node.cond.accept(self)

        string = 'WHILE %s DO BEGIN' % cond
        self.scope += 1
        string += self.new_line()
        string += node.body.accept(self)
        self.scope -= 1
        string += self.new_line()
        string += 'END'

        return string

    def visit_RepeatNode(self, node, arg=None):
        assert isinstance(node, ast.RepeatNode)

        string = 'REPEAT'
        self.scope += 1
        string += self.new_line()
        string += node.body.accept(self)
        self.scope -= 1
        string += self.new_line()
        string += 'UNTIL %s' % node.cond.accept(self)

        return string

    def visit_ForNode(self, node, arg=None):
        assert isinstance(node, ast.ForNode)

        var = node.var.accept(self)
        start = node.value_start.accept(self)
        stop = node.value_end.accept(self)
        d = node.direction.upper()

        string = 'FOR %s := %s %s %s DO BEGIN' % (var, start, d, stop)

        self.scope += 1
        string += self.new_line()
        string += node.body.accept(self)
        self.scope -= 1

        string += self.new_line()
        string += 'END'

        return string

    def visit_CaseStatementNode(self, node, arg=None):
        assert isinstance(node, ast.CaseStatementNode)

        string = 'CASE %s OF' % node.case_index.accept(self)
        self.scope += 1
        string += self.new_line()

        if node.case_list_element_list:
            string += node.case_list_element_list.accept(self)
            string += self.new_line()

        string += 'OTHERWISE'
        if node.otherwise:
            string += ' BEGIN'
            self.scope += 1
            string += self.new_line()

            string += node.otherwise.accept(self)

            self.scope += -1
            string += self.new_line()
            string += 'END;'
        else:
            string += ' ;'

        self.scope += -1
        string += self.new_line()
        string += 'END (* CASE *)'

        return string

    def visit_CaseListElementNode(self, node, arg=None):
        assert isinstance(node, ast.CaseListElementNode)

        string = '%s: BEGIN' % node.case_constant_list.accept(self)
        self.scope += 1
        string += self.new_line()

        if node.statement:
            string += node.statement.accept(self)
        else:
            string += '(* NOP *)'

        self.scope -= 1
        string += self.new_line()
        string += 'END'

        return string

    def visit_GotoNode(self, node, arg=None):
        assert isinstance(node, ast.GotoNode)

        return 'GOTO %s' % node.label.accept(self)

    def visit_AssignmentNode(self, node, arg=None):
        assert isinstance(node, ast.AssignmentNode)

        var = node.var_access.accept(self)
        value = node.expr.accept(self)

        return '%s := %s' % (var, value)

    def visit_FunctionCallNode(self, node, arg=None):
        assert isinstance(node, ast.FunctionCallNode)

        name = node.identifier.accept(self)
        if node.arg_list:
            args = node.arg_list.accept(self)
        else:
            args = ''

        return name + args

    def visit_ArgumentNode(self, node, params=None):
        assert isinstance(node, ast.ArgumentNode)

        return node.expr.accept(self)

    def visit_LabeledStatementNode(self, node, arg=None):
        assert isinstance(node, ast.LabeledStatementNode)

        label = node.label.accept(self)
        stmt = node.stmt.accept(self)

        return '%s: %s' % (label, stmt)

    def visit_IntegerNode(self, node, arg=None):
        assert isinstance(node, ast.IntegerNode)

        return str(node.value)

    def visit_RealNode(self, node, arg=None):
        assert isinstance(node, ast.RealNode)

        return str(node.value)

    def visit_StringNode(self, node, arg=None):
        assert isinstance(node, ast.StringNode)

        string = node.value
        string = string.replace('\n', '\\n')
        string = string.replace('\t', '\\t')
        string = string.replace('\r', '\\r')

        return "'%s'" % string

    def visit_CharNode(self, node, arg=None):
        assert isinstance(node, ast.CharNode)

        return "'%s'" % str(node.value)

    def visit_SetMemberRangeNode(self, node, arg=None):
        assert isinstance(node, ast.SetMemberRangeNode)

        member = node.member.accept(self)
        expr = node.expr.accept(self)

        return '%s..%s' % (member, expr)

    def visit_SetNode(self, node, arg=None):
        assert isinstance(node, ast.SetNode)

        members = node.member_list.accept(self)

        return '[%s]' % members

    def visit_SetEmptyNode(self, node, arg=None):
        assert isinstance(node, ast.SetEmptyNode)

        return '[]'

    def visit_IdentifierNode(self, node, arg=None):
        assert isinstance(node, ast.IdentifierNode)

        return node.name

    def visit_RangeNode(self, node, arg=None):
        assert isinstance(node, ast.RangeNode)

        lo = node.start.accept(self)
        hi = node.stop.accept(self)

        return '%s..%s' % (lo, hi)

    def visit_CaseConstNode(self, node, arg=None):
        assert isinstance(node, ast.CaseConstNode)

        return node.constant.accept(self)

    def visit_CaseRangeNode(self, node, arg=None):
        assert isinstance(node, ast.CaseRangeNode)

        first = node.first_constant.accept(self)
        last = node.last_constant.accept(self)

        return '%s..%s' % (first, last)

    def visit_ConstDeclNode(self, node, arg=None):
        assert isinstance(node, ast.ConstDeclNode)

        expr = node.expr.accept(self)
        name = node.identifier.accept(self)

        return '%s = %s' % (name, expr)

    def visit_EnumTypeNode(self, node, arg=None):
        assert isinstance(node, ast.EnumTypeNode)

        names = node.identifier_list.accept(self)
        if node.attr:
            attr = '(*.' + node.attr.accept(self) + '.*) '
        else:
            attr = ''

        return '%s(%s)' % (attr, names)

    def visit_SetTypeNode(self, node, arg=None):
        assert isinstance(node, ast.SetTypeNode)

        base = node.base_type.accept(self)

        return 'SET OF %s' % base

    def visit_TypeNode(self, node, arg=None):
        assert isinstance(node, ast.TypeNode)

        name = node.identifier.accept(self)
        if node.attr:
            attr = '(*.' + node.attr.accept(self) + '.*) '
        else:
            attr = ''

        return attr + name

    def visit_ArrayTypeNode(self, node, arg=None):
        assert isinstance(node, ast.ArrayTypeNode)

        component = node.component_type.accept(self)
        dims = node.index_list.accept(self)

        return 'ARRAY[%s] OF %s' % (dims, component)

    def visit_PointerTypeNode(self, node, arg=None):
        assert isinstance(node, ast.PointerTypeNode)

        return '^%s' % node.domain_type.accept(self)

    def visit_NullNode(self, node, ty):
        assert isinstance(node, ast.NullNode)

        return 'NIL'

    def visit_FileTypeNode(self, node, arg=None):
        assert isinstance(node, ast.FileTypeNode)

        return 'FILE OF ' % node.component_type.accept(self)

    def visit_TypeDeclNode(self, node, arg=None):
        assert isinstance(node, ast.TypeDeclNode)

        name = node.identifier.accept(self)
        ty = node.type_denoter.accept(self)

        return '%s = %s' % (name, ty)

    def visit_VarDeclNode(self, node, arg=None):
        assert isinstance(node, ast.VarDeclNode)

        ty = node.type_denoter.accept(self)
        names = node.identifier_list.accept(self)
        return '%s : %s' % (names, ty)

    def visit_LabelNode(self, node, arg=None):
        assert isinstance(node, ast.LabelNode)

        return node.name

    def visit_LabelDeclNode(self, node, arg=None):
        assert isinstance(node, ast.LabelDeclNode)

        string = self.new_line()
        string += 'LABEL'

        self.scope += 1
        string += self.new_line()

        for c in node.children:
            string += c.accept(self) + ';'
            string += self.new_line()

        self.scope -= 1
        return string

    def visit_FunctionHeadNode(self, node, arg=None):
        assert isinstance(node, ast.FunctionHeadNode)

        name = node.identifier.accept(self)
        ret_ty = node.return_type.accept(self)

        if node.param_list:
            params = node.param_list.accept(self)
            return '%s(%s) : %s' % (name, params, ret_ty)
        else:
            return '%s : %s' % (name, ret_ty)

    def visit_ValueParameterNode(self, node, arg=None):
        assert isinstance(node, ast.ValueParameterNode)

        names = node.identifier_list.accept(self)
        type_name = node.type_denoter.accept(self)

        return '%s : %s' % (names, type_name)

    def visit_RefParameterNode(self, node, arg=None):
        assert isinstance(node, ast.RefParameterNode)

        names = node.identifier_list.accept(self)
        type_name = node.type_denoter.accept(self)

        return 'VAR %s : %s' % (names, type_name)

    def visit_ProcedureHeadNode(self, node, arg=None):
        assert isinstance(node, ast.ProcedureHeadNode)

        name = node.identifier.accept(self)
        if node.param_list:
            params = node.param_list.accept(self)
            return '%s(%s)' % (name, params)
        else:
            return name

    def visit_RecordTypeNode(self, node, record_name):
        assert isinstance(node, ast.RecordTypeNode)

        string = 'RECORD'
        self.scope += 1
        string += self.new_line()

        if node.section_list:
            string += node.section_list.accept(self) + ';'
            string += self.new_line()

        if node.variant:
            string += node.variant.accept(self) + ';'

        self.scope -= 1
        string += self.new_line()
        string += 'END (* RECORD *)'

        return string

    def visit_RecordSectionNode(self, node, siblings):
        assert isinstance(node, ast.RecordSectionNode)

        names = node.identifier_list.accept(self)
        ty = node.type_denoter.accept(self)

        return '%s : %s' % (names, ty)

    def visit_VariantPartNode(self, node, rec):
        assert isinstance(node, ast.VariantPartNode)

        selector = node.variant_selector.accept(self)

        string = 'CASE %s OF' % selector

        self.scope += 1
        string += self.new_line()
        string += node.variant_list.accept(self)
        self.scope -= 1

        return string

    def visit_VariantSelectorNode(self, node, arg=None):
        assert isinstance(node, ast.VariantSelectorNode)

        ty = node.tag_type.accept(self)

        if node.tag_field:
            field = node.tag_field.accept(self)
            return '%s: %s' % (field, ty)
        else:
            return ty

    def visit_VariantNode(self, node, arg=None):
        assert isinstance(node, ast.VariantNode)

        cases = node.case_list.accept(self)

        string = '%s: (' % cases

        if node.variant_part:
            string += node.variant_part.accept(self)

        if node.record_list:
            string += node.record_list.accept(self, True)

        string += ')'

        return string

    def visit_RecordSectionListNode(self, node, variant=False):
        assert isinstance(node, ast.RecordSectionListNode)

        string = ''
        prefix = ''
        for c in node.children:
            string += prefix + c.accept(self)

            if not variant:
                prefix = ';' + self.new_line()
            else:
                prefix = ';'

        return string

    def visit_VariantListNode(self, node, arg):
        assert isinstance(node, ast.VariantListNode)

        string = ''
        prefix = ''
        for c in node.children:
            string += prefix + c.accept(self)
            prefix = ';' + self.new_line()

        return string

    def visit_ArgumentListNode(self, node, arg):
        assert isinstance(node, ast.ArgumentListNode)

        names = ''
        prefix = ''
        for c in node.children:
            names += prefix + c.accept(self)
            prefix = ', '

        return '(%s)' % names

    def visit_IdentifierListNode(self, node, arg=None):
        assert isinstance(node, ast.IdentifierListNode)

        names = ''
        prefix = ''
        for c in node.children:
            names += prefix + c.accept(self)
            prefix = ', '

        return names

    def visit_LabelListNode(self, node, arg):
        assert isinstance(node, ast.LabelListNode)

        cases = ''
        prefix = ''
        for c in node.children:
            cases += prefix + c.accept(self)
            prefix = ', '

        return cases

    def visit_IndexListNode(self, node, arg):
        assert isinstance(node, ast.IndexListNode)

        string = ''
        prefix = ''
        for c in node.children:
            string += prefix + c.accept(self)
            prefix = ', '

        return string

    def visit_ParameterListNode(self, node, arg):
        assert isinstance(node, ast.ParameterListNode)

        string = ''
        prefix = ''
        for c in node.children:
            string += prefix + c.accept(self)
            prefix = '; '

        return string

    def visit_VarDeclListNode(self, node, arg=None):
        assert isinstance(node, ast.VarDeclListNode)

        string = self.new_line()
        string += 'VAR'

        self.scope += 1
        string += self.new_line()

        for c in node.children:
            string += c.accept(self) + ';'
            string += self.new_line()

        self.scope -= 1

        return string

    def visit_CaseListElementListNode(self, node, arg):
        assert isinstance(node, ast.CaseListElementListNode)

        string = ''
        for c in node.children:
            string += c.accept(self, arg) + ';'
            string += self.new_line()

        return string

    def visit_CaseConstListNode(self, node, arg):
        assert isinstance(node, ast.CaseConstListNode)

        string = ''
        prefix = ''
        for c in node.children:
            string += prefix + c.accept(self)
            prefix = ', '

        return string

    def visit_SetMemberListNode(self, node, arg):
        assert isinstance(node, ast.SetMemberListNode)

        string = ''
        prefix = ''
        for c in node.children:
            string += prefix + c.accept(self)
            prefix = ', '

        return string

    def visit_TypeDeclListNode(self, node, arg=None):
        assert isinstance(node, ast.TypeDeclListNode)

        string = self.new_line()
        string += 'TYPE'

        self.scope += 1
        string += self.new_line()

        for c in node.children:
            string += c.accept(self) + ';'
            string += self.new_line()

        self.scope -= 1

        return string

    def visit_ConstListNode(self, node, arg=None):
        assert isinstance(node, ast.ConstListNode)

        string = self.new_line()
        string += 'CONST'

        self.scope += 1
        string += self.new_line()

        for c in node.children:
            string += c.accept(self) + ';'
            string += self.new_line()

        self.scope -= 1

        return string

    def visit_StatementListNode(self, node, arg=None):
        assert isinstance(node, ast.StatementListNode)

        string = ''

        for c in node.children:
            string += c.accept(self) + ';'
            string += self.new_line()

        return string
