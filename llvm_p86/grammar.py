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
Grammar rules and parser for Pascal-86

Initially generated with yply from:
  http://ply.googlecode.com/svn/trunk/example/yply

Grammar rules originally taken from:
  http://www.moorecad.com/standardpascal/pascal.y
'''

import os
from ply import yacc

from . import log
from .ast import *
from .tokens import *


precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'STAR', 'SLASH'),
    ('left', 'DIV', 'MOD'),
    ('left', 'EQUAL', 'NOTEQUAL', 'LE', 'LT', 'GT', 'GE'),
    ('left', 'OR', 'AND')
)


# The first set of rules are VAX pascal only!


def p_input_1(p):
    '''input : inherit file'''
    p[0] = p[2]


def p_inherit_1(p):
    '''inherit : LBRAC INHERIT LPAREN string_list RPAREN RBRAC'''
    pass


def p_inherit_2(p):
    '''inherit : empty'''
    pass


def p_string_list_1(p):
    '''string_list : STRING comma string_list'''
    pass


def p_string_list_2(p):
    '''string_list : STRING'''
    pass


def p_array_type_2(p):
    '''array_type : VARYING LBRAC index_list RBRAC OF component_type '''
    p[0] = ArrayTypeNode(p[3], p[6])
    p[0].pos_info = get_pos(p, 0)


def p_attr_1(p):
    '''attr : LBRAC identifier_list RBRAC'''
    p[0] = p[2]


def p_attr_2(p):
    '''attr : LPAREN DOT identifier_list DOT RPAREN'''
    p[0] = p[3]


def p_type_denoter_3(p):
    '''type_denoter : attr identifier'''
    p[0] = TypeNode(p[2], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_enumerated_type_2(p):
    '''enumerated_type : attr LPAREN identifier_list RPAREN'''
    p[0] = EnumTypeNode(p[3], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_proc_or_func_declaration_3(p):
    '''proc_or_func_declaration : attr procedure_declaration'''
    p[0] = p[2]
    p[0].attr = p[1]


def p_proc_or_func_declaration_4(p):
    '''proc_or_func_declaration : attr function_declaration'''
    p[0] = p[2]
    p[0].attr = p[1]


def p_value_parameter_specification_2(p):
    '''value_parameter_specification : identifier_list COLON array_type'''
    p[0] = ValueParameterNode(p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_variable_parameter_specification_2(p):
    '''
    variable_parameter_specification : VAR identifier_list COLON array_type
    '''
    p[0] = RefParameterNode(p[2], p[4])
    p[0].pos_info = get_pos(p, 0)


def p_new_ordinal_type_3(p):
    '''new_ordinal_type : unsigned_number'''
    p[0] = p[1]


# Pascal-86


def p_file_1(p):
    '''file : program'''
    p[0] = p[1]


def p_file_2(p):
    '''file : module'''
    p[0] = p[1]


def p_program_1(p):
    '''
    program : PROGRAM identifier LPAREN identifier_list RPAREN semicolon block DOT
    '''
    p[0] = ProgramNode(p[2], p[7], p[4])
    p[0].pos_info = get_pos(p, 0)


def p_program_2(p):
    '''program : PROGRAM identifier semicolon block DOT'''
    p[0] = ProgramNode(p[2], p[4])
    p[0].pos_info = get_pos(p, 0)


def p_module_1(p):
    '''module : MODULE identifier semicolon interface program'''
    p[0] = ModuleNode(p[5], p[2], p[4])
    p[0].pos_info = get_pos(p, 0)


def p_module_2(p):
    '''module : MODULE identifier semicolon interface non_main'''
    p[0] = ModuleNode(p[5], p[2], p[4])
    p[0].pos_info = get_pos(p, 0)


def p_subsection_1(p):
    '''subsection : for_declaration_part label_declaration_part constant_definition_part type_definition_part variable_declaration_part public_procedure_and_function_declaration_part'''
    p[0] = SectionNode(p[1], p[2], p[3], p[4], p[5], p[6])
    p[0].pos_info = get_pos(p, 0)


def p_for_declaration_part_1(p):
    '''for_declaration_part : FOR identifier_list semicolon'''
    # TODO: p_for_declaration_part_1
    pass


def p_for_declaration_part_2(p):
    '''for_declaration_part : empty'''
    pass


def p_public_procedure_and_function_declaration_part_1(p):
    '''public_procedure_and_function_declaration_part : public_proc_or_func_declaration_list semicolon'''
    p[0] = p[1]


def p_public_procedure_and_function_declaration_part_2(p):
    '''public_procedure_and_function_declaration_part : empty'''
    p[0] = p[1]


def p_public_proc_or_func_declaration_list_1(p):
    '''public_proc_or_func_declaration_list : public_proc_or_func_declaration_list semicolon public_proc_or_func_declaration'''
    p[0] = FunctionListNode(p[3], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_public_proc_or_func_declaration_list_2(p):
    '''public_proc_or_func_declaration_list : public_proc_or_func_declaration'''
    p[0] = FunctionListNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_public_proc_or_func_declaration_1(p):
    '''public_proc_or_func_declaration : public_procedure_declaration'''
    p[0] = p[1]


def p_public_proc_or_func_declaration_2(p):
    '''public_proc_or_func_declaration : public_function_declaration'''
    p[0] = p[1]


def p_public_procedure_declaration_1(p):
    '''public_procedure_declaration : procedure_heading'''
    p[0] = PublicProcedureNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_public_function_declaration_1(p):
    '''public_function_declaration : function_heading'''
    p[0] = PublicFunctionNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_interface_1(p):
    '''interface : interface public_section'''
    p[0] = PublicSectionListNode(p[2], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_interface_2(p):
    '''interface : public_section'''
    p[0] = PublicSectionListNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_interface_3(p):
    '''interface : empty'''
    pass


def p_public_section_1(p):
    '''public_section : PUBLIC identifier semicolon subsection'''
    p[0] = PublicSectionNode(p[2], p[4])
    p[0].pos_info = get_pos(p, 0)


def p_non_main_1(p):
    '''non_main : PRIVATE identifier semicolon constant_definition_part type_definition_part variable_declaration_part procedure_and_function_declaration_part DOT'''
    p[0] = NonMainNode(p[2], p[4], p[5], p[6], p[7])
    p[0].pos_info = get_pos(p, 0)


def p_identifier_list_1(p):
    '''identifier_list : identifier_list comma identifier'''
    p[0] = IdentifierListNode(p[3], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_identifier_list_2(p):
    '''identifier_list : identifier'''
    p[0] = IdentifierListNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_block_1(p):
    '''block : label_declaration_part constant_definition_part type_definition_part variable_declaration_part procedure_and_function_declaration_part statement_part'''
    p[0] = BlockNode(p[1], p[2], p[3], p[4], p[5], p[6])
    p[0].pos_info = get_pos(p, 0)


def p_label_declaration_part_1(p):
    '''label_declaration_part : LABEL label_list semicolon'''
    p[0] = LabelDeclNode(p[2])
    p[0].pos_info = get_pos(p, 0)


def p_label_declaration_part_2(p):
    '''label_declaration_part : empty'''
    pass


def p_label_list_1(p):
    '''label_list : label_list comma label'''
    p[0] = LabelListNode(p[3], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_label_list_2(p):
    '''label_list : label'''
    p[0] = LabelListNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_label_1(p):
    '''label : DIGSEQ'''
    p[0] = LabelNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_constant_definition_part_1(p):
    '''constant_definition_part : CONST constant_list'''
    p[0] = p[2]


def p_constant_definition_part_2(p):
    '''constant_definition_part : empty'''
    pass


def p_constant_list_1(p):
    '''constant_list : constant_list constant_definition'''
    p[0] = ConstListNode(p[2], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_constant_list_2(p):
    '''constant_list : constant_definition'''
    p[0] = ConstListNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_constant_definition_1(p):
    '''constant_definition : identifier EQUAL cexpression semicolon'''
    p[0] = ConstDeclNode(p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_cexpression_1(p):
    '''cexpression : csimple_expression'''
    p[0] = p[1]


def p_cexpression_2(p):
    '''cexpression : csimple_expression relop csimple_expression'''
    p[0] = BinaryOpNode(p[2], p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_csimple_expression_1(p):
    '''csimple_expression : cterm'''
    p[0] = p[1]


def p_csimple_expression_2(p):
    '''csimple_expression : csimple_expression addop cterm'''
    p[0] = BinaryOpNode(p[2], p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_cterm_1(p):
    '''cterm : cfactor'''
    p[0] = p[1]


def p_cterm_2(p):
    '''cterm : cterm mulop cfactor'''
    p[0] = BinaryOpNode(p[2], p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_cfactor_1(p):
    '''cfactor : sign cfactor'''
    p[0] = UnaryOpNode(p[1], p[2])
    p[0].pos_info = get_pos(p, 0)


def p_cfactor_2(p):
    '''cfactor : cprimary'''
    p[0] = p[1]


def p_cprimary_1(p):
    '''cprimary : identifier'''
    p[0] = VarAccessNode(p[1])


def p_cprimary_2(p):
    '''cprimary : LPAREN cexpression RPAREN'''
    p[0] = p[2]


def p_cprimary_3(p):
    '''cprimary : unsigned_constant'''
    p[0] = p[1]


def p_cprimary_4(p):
    '''cprimary : NOT cprimary'''
    p[0] = UnaryOpNode(p[1].lower(), p[2])
    p[0].pos_info = get_pos(p, 0)


def p_constant_1(p):
    '''constant : non_string'''
    p[0] = p[1]


def p_constant_2(p):
    '''constant : sign non_string'''
    p[0] = UnaryOpNode(p[1], p[2])
    p[0].pos_info = get_pos(p, 0)


def p_constant_3(p):
    '''constant : STRING'''
    p[0] = StringNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_constant_4(p):
    '''constant : CHAR'''
    p[0] = CharNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_sign_1(p):
    '''sign : PLUS'''
    p[0] = p[1]


def p_sign_2(p):
    '''sign : MINUS'''
    p[0] = p[1]


def p_non_string_1(p):
    '''non_string : DIGSEQ'''
    p[0] = IntegerNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_non_string_2(p):
    '''non_string : identifier'''
    p[0] = VarAccessNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_non_string_3(p):
    '''non_string : REALNUMBER'''
    p[0] = RealNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_type_definition_part_1(p):
    '''type_definition_part : TYPE type_definition_list'''
    p[0] = p[2]


def p_type_definition_part_2(p):
    '''type_definition_part : empty'''
    pass


def p_type_definition_list_1(p):
    '''type_definition_list : type_definition_list type_definition'''
    p[0] = TypeDeclListNode(p[2], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_type_definition_list_2(p):
    '''type_definition_list : type_definition'''
    p[0] = TypeDeclListNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_type_definition_1(p):
    '''type_definition : identifier EQUAL type_denoter semicolon'''
    p[0] = TypeDeclNode(p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_type_denoter_1(p):
    '''type_denoter : identifier'''
    p[0] = TypeNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_type_denoter_2(p):
    '''type_denoter : new_type'''
    p[0] = p[1]


def p_new_type_1(p):
    '''new_type : new_ordinal_type'''
    p[0] = p[1]


def p_new_type_2(p):
    '''new_type : new_structured_type'''
    p[0] = p[1]


def p_new_type_3(p):
    '''new_type : new_pointer_type'''
    p[0] = p[1]


def p_new_ordinal_type_1(p):
    '''new_ordinal_type : enumerated_type'''
    p[0] = p[1]


def p_new_ordinal_type_2(p):
    '''new_ordinal_type : subrange_type'''
    p[0] = p[1]


def p_enumerated_type_1(p):
    '''enumerated_type : LPAREN identifier_list RPAREN'''
    p[0] = EnumTypeNode(p[2])
    p[0].pos_info = get_pos(p, 0)


def p_subrange_type_1(p):
    '''subrange_type : constant DOTDOT constant'''
    p[0] = RangeNode(p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_new_structured_type_1(p):
    '''new_structured_type : structured_type'''
    p[0] = p[1]


def p_new_structured_type_2(p):
    '''new_structured_type : PACKED structured_type'''
    p[0] = p[2]
    # TODO: packed structures


def p_structured_type_1(p):
    '''structured_type : array_type'''
    p[0] = p[1]


def p_structured_type_2(p):
    '''structured_type : record_type'''
    p[0] = p[1]


def p_structured_type_3(p):
    '''structured_type : set_type'''
    p[0] = p[1]


def p_structured_type_4(p):
    '''structured_type : file_type'''
    p[0] = p[1]
    # TODO: implement file support


def p_array_type_1(p):
    '''array_type : ARRAY LBRAC index_list RBRAC OF component_type'''
    p[0] = ArrayTypeNode(p[3], p[6])
    p[0].pos_info = get_pos(p, 0)


def p_index_list_1(p):
    '''index_list : index_list comma index_type'''
    p[0] = IndexListNode(p[3], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_index_list_2(p):
    '''index_list : index_type'''
    p[0] = IndexListNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_index_type_1(p):
    '''index_type : ordinal_type'''
    p[0] = p[1]


def p_ordinal_type_1(p):
    '''ordinal_type : new_ordinal_type'''
    p[0] = p[1]


def p_ordinal_type_2(p):
    '''ordinal_type : identifier'''
    p[0] = TypeNode(p[1])


def p_component_type_1(p):
    '''component_type : type_denoter'''
    p[0] = p[1]


def p_record_type_1(p):
    '''record_type : RECORD record_section_list END'''
    p[0] = RecordTypeNode(p[2], None)
    p[0].pos_info = get_pos(p, 0)


def p_record_type_2(p):
    '''record_type : RECORD record_section_list semicolon variant_part END'''
    p[0] = RecordTypeNode(p[2], p[4])
    p[0].pos_info = get_pos(p, 0)


def p_record_type_3(p):
    '''record_type : RECORD variant_part END'''
    p[0] = RecordTypeNode(None, p[2])
    p[0].pos_info = get_pos(p, 0)


def p_record_section_list_1(p):
    '''record_section_list : record_section_list semicolon record_section'''
    p[0] = RecordSectionListNode(p[3], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_record_section_list_2(p):
    '''record_section_list : record_section'''
    p[0] = RecordSectionListNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_record_section_1(p):
    '''record_section : identifier_list COLON type_denoter'''
    p[0] = RecordSectionNode(p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_variant_selector_1(p):
    '''variant_selector : tag_field COLON tag_type'''
    p[0] = VariantSelectorNode(p[3], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_variant_selector_2(p):
    '''variant_selector : tag_type'''
    p[0] = VariantSelectorNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_variant_list_1(p):
    '''variant_list : variant_list semicolon variant'''
    p[0] = VariantListNode(p[3], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_variant_list_2(p):
    '''variant_list : variant'''
    p[0] = VariantListNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_variant_1(p):
    '''variant : case_constant_list COLON LPAREN record_section_list RPAREN'''
    p[0] = VariantNode(p[1], p[4], None)
    p[0].pos_info = get_pos(p, 0)


def p_variant_2(p):
    '''variant : case_constant_list COLON LPAREN record_section_list semicolon variant_part RPAREN'''
    p[0] = VariantNode(p[1], p[4], p[6])
    p[0].pos_info = get_pos(p, 0)


def p_variant_3(p):
    '''variant : case_constant_list COLON LPAREN variant_part RPAREN'''
    p[0] = VariantNode(p[1], None, p[4])
    p[0].pos_info = get_pos(p, 0)


def p_variant_part_1(p):
    '''variant_part : CASE variant_selector OF variant_list'''
    p[0] = VariantPartNode(p[2], p[4])
    p[0].pos_info = get_pos(p, 0)


def p_variant_part_2(p):
    '''variant_part : CASE variant_selector OF variant_list semicolon'''
    p[0] = VariantPartNode(p[2], p[4])
    p[0].pos_info = get_pos(p, 0)


def p_variant_part_3(p):
    '''variant_part : empty'''
    pass


def p_case_constant_list_1(p):
    '''case_constant_list : case_constant_list comma case_constant'''
    p[0] = CaseConstListNode(p[3], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_case_constant_list_2(p):
    '''case_constant_list : case_constant'''
    p[0] = CaseConstListNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_case_constant_1(p):
    '''case_constant : constant'''
    p[0] = CaseConstNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_case_constant_2(p):
    '''case_constant : constant DOTDOT constant'''
    p[0] = CaseRangeNode(p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_tag_field_1(p):
    '''tag_field : identifier'''
    p[0] = p[1]


def p_tag_type_1(p):
    '''tag_type : identifier'''
    p[0] = p[1]


def p_set_type_1(p):
    '''set_type : SET OF base_type'''
    p[0] = SetTypeNode(p[3])
    p[0].pos_info = get_pos(p, 0)


def p_base_type_1(p):
    '''base_type : ordinal_type'''
    p[0] = p[1]


def p_file_type_1(p):
    '''file_type : PFILE OF component_type'''
    p[0] = FileTypeNode(p[3])
    p[0].pos_info = get_pos(p, 0)


def p_new_pointer_type_1(p):
    '''new_pointer_type : UPARROW domain_type'''
    p[0] = PointerTypeNode(p[2])
    p[0].pos_info = get_pos(p, 0)


def p_domain_type_1(p):
    '''domain_type : identifier'''
    p[0] = TypeNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_variable_declaration_part_1(p):
    '''variable_declaration_part : VAR variable_declaration_list semicolon'''
    p[0] = p[2]


def p_variable_declaration_part_2(p):
    '''variable_declaration_part : empty'''
    pass


def p_variable_declaration_list_1(p):
    '''variable_declaration_list : variable_declaration_list semicolon variable_declaration'''
    p[0] = VarDeclListNode(p[3], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_variable_declaration_list_2(p):
    '''variable_declaration_list : variable_declaration'''
    p[0] = VarDeclListNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_variable_declaration_1(p):
    '''variable_declaration : identifier_list COLON type_denoter'''
    p[0] = VarDeclNode(p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_procedure_and_function_declaration_part_1(p):
    '''procedure_and_function_declaration_part : proc_or_func_declaration_list semicolon'''
    p[0] = p[1]


def p_procedure_and_function_declaration_part_2(p):
    '''procedure_and_function_declaration_part : empty'''
    pass


def p_proc_or_func_declaration_list_1(p):
    '''proc_or_func_declaration_list : proc_or_func_declaration_list semicolon proc_or_func_declaration'''
    p[0] = FunctionListNode(p[3], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_proc_or_func_declaration_list_2(p):
    '''proc_or_func_declaration_list : proc_or_func_declaration'''
    p[0] = FunctionListNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_proc_or_func_declaration_1(p):
    '''proc_or_func_declaration : procedure_declaration'''
    p[0] = p[1]


def p_proc_or_func_declaration_2(p):
    '''proc_or_func_declaration : function_declaration'''
    p[0] = p[1]


def p_procedure_declaration_1(p):
    '''procedure_declaration : procedure_heading semicolon procedure_block'''
    p[0] = ProcedureNode(p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_procedure_heading_1(p):
    '''procedure_heading : procedure_identification'''
    p[0] = ProcedureHeadNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_procedure_heading_2(p):
    '''procedure_heading : procedure_identification formal_parameter_list'''
    p[0] = ProcedureHeadNode(p[1], p[2])
    p[0].pos_info = get_pos(p, 0)


def p_formal_parameter_list_1(p):
    '''formal_parameter_list : LPAREN formal_parameter_section_list RPAREN'''
    p[0] = p[2]


def p_formal_parameter_section_list_1(p):
    '''formal_parameter_section_list : formal_parameter_section_list semicolon formal_parameter_section'''
    p[0] = ParameterListNode(p[3], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_formal_parameter_section_list_2(p):
    '''formal_parameter_section_list : formal_parameter_section'''
    p[0] = ParameterListNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_formal_parameter_section_1(p):
    '''formal_parameter_section : value_parameter_specification'''
    p[0] = p[1]


def p_formal_parameter_section_2(p):
    '''formal_parameter_section : variable_parameter_specification'''
    p[0] = p[1]


def p_formal_parameter_section_3(p):
    '''formal_parameter_section : procedural_parameter_specification'''
    p[0] = p[1]


def p_formal_parameter_section_4(p):
    '''formal_parameter_section : functional_parameter_specification'''
    p[0] = p[1]


def p_value_parameter_specification_1(p):
    '''value_parameter_specification : identifier_list COLON identifier'''
    p[0] = ValueParameterNode(p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_variable_parameter_specification_1(p):
    '''
    variable_parameter_specification : VAR identifier_list COLON identifier
    '''
    p[0] = RefParameterNode(p[2], p[4])
    p[0].pos_info = get_pos(p, 0)


def p_procedural_parameter_specification_1(p):
    '''procedural_parameter_specification : procedure_heading'''
    p[0] = p[1]
    # TODO: procedure as argument


def p_functional_parameter_specification_1(p):
    '''functional_parameter_specification : function_heading'''
    p[0] = p[1]
    # TODO: function as argument


def p_procedure_identification_1(p):
    '''procedure_identification : PROCEDURE identifier'''
    p[0] = p[2]


def p_procedure_block_1(p):
    '''procedure_block : block'''
    p[0] = p[1]


def p_function_declaration_1(p):
    '''
    function_declaration : function_identification semicolon function_block
    '''
    p[0] = ProcedureNode(p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_function_declaration_2(p):
    '''function_declaration : function_heading semicolon function_block'''
    p[0] = FunctionNode(p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_function_heading_1(p):
    '''function_heading : FUNCTION identifier COLON result_type'''
    p[0] = FunctionHeadNode(p[4], p[2])
    p[0].pos_info = get_pos(p, 0)


def p_function_heading_2(p):
    '''function_heading : FUNCTION identifier formal_parameter_list COLON result_type'''
    p[0] = FunctionHeadNode(p[5], p[2], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_result_type_1(p):
    '''result_type : identifier'''
    p[0] = TypeNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_function_identification_1(p):
    '''function_identification : FUNCTION identifier'''
    p[0] = ProcedureHeadNode(p[2])
    p[0].pos_info = get_pos(p, 0)


def p_function_block_1(p):
    '''function_block : block'''
    p[0] = p[1]


def p_statement_part_1(p):
    '''statement_part : compound_statement'''
    p[0] = p[1]


def p_compound_statement_1(p):
    '''compound_statement : PBEGIN statement_sequence END'''
    p[0] = p[2]


def p_statement_sequence_1(p):
    '''statement_sequence : statement_sequence semicolon statement'''
    p[0] = StatementListNode(p[3], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_statement_sequence_2(p):
    '''statement_sequence : statement'''
    p[0] = StatementListNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_statement_1(p):
    '''statement : open_statement'''
    p[0] = p[1]


def p_statement_2(p):
    '''statement : closed_statement'''
    p[0] = p[1]


def p_open_statement_1(p):
    '''open_statement : label COLON non_labeled_open_statement'''
    p[0] = LabeledStatementNode(p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_open_statement_2(p):
    '''open_statement : non_labeled_open_statement'''
    p[0] = p[1]


def p_closed_statement_1(p):
    '''closed_statement : label COLON non_labeled_closed_statement'''
    p[0] = LabeledStatementNode(p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_closed_statement_2(p):
    '''closed_statement : non_labeled_closed_statement'''
    p[0] = p[1]


def p_non_labeled_open_statement_1(p):
    '''non_labeled_open_statement : open_with_statement'''
    p[0] = p[1]


def p_non_labeled_open_statement_2(p):
    '''non_labeled_open_statement : open_if_statement'''
    p[0] = p[1]


def p_non_labeled_open_statement_3(p):
    '''non_labeled_open_statement : open_while_statement'''
    p[0] = p[1]


def p_non_labeled_open_statement_4(p):
    '''non_labeled_open_statement : open_for_statement'''
    p[0] = p[1]


def p_non_labeled_closed_statement(p):
    """
    non_labeled_closed_statement : assignment_statement
    | procedure_statement
    | goto_statement
    | compound_statement
    | case_statement
    | repeat_statement
    | closed_with_statement
    | closed_if_statement
    | closed_while_statement
    | closed_for_statement
    | empty
    """
    if len(p) == 2:
        p[0] = StatementListNode(p[1])
        p[0].pos_info = get_pos(p, 0)


def p_repeat_statement_1(p):
    '''repeat_statement : REPEAT statement_sequence UNTIL boolean_expression'''
    p[0] = RepeatNode(p[2], p[4])
    p[0].pos_info = get_pos(p, 0)


def p_open_while_statement_1(p):
    '''open_while_statement : WHILE boolean_expression DO open_statement'''
    p[0] = WhileNode(p[2], p[4])
    p[0].pos_info = get_pos(p, 0)


def p_closed_while_statement_1(p):
    '''closed_while_statement : WHILE boolean_expression DO closed_statement'''
    p[0] = WhileNode(p[2], p[4])
    p[0].pos_info = get_pos(p, 0)


def p_open_for_statement_1(p):
    '''open_for_statement : FOR control_variable ASSIGNMENT initial_value direction final_value DO open_statement'''
    p[0] = ForNode(p[2], p[4], p[5].lower(), p[6], p[8])
    p[0].pos_info = get_pos(p, 0)


def p_closed_for_statement_1(p):
    '''closed_for_statement : FOR control_variable ASSIGNMENT initial_value direction final_value DO closed_statement'''
    p[0] = ForNode(p[2], p[4], p[5].lower(), p[6], p[8])
    p[0].pos_info = get_pos(p, 0)


def p_open_with_statement_1(p):
    '''open_with_statement : WITH record_variable_list DO open_statement'''
    p[0] = WithNode(p[2], p[4])
    p[0].pos_info = get_pos(p, 0)


def p_closed_with_statement_1(p):
    '''closed_with_statement : WITH record_variable_list DO closed_statement'''
    p[0] = WithNode(p[2], p[4])
    p[0].pos_info = get_pos(p, 0)


def p_open_if_statement_1(p):
    '''open_if_statement : IF boolean_expression THEN statement'''
    p[0] = IfNode(p[2], p[4])
    p[0].pos_info = get_pos(p, 0)


def p_open_if_statement_2(p):
    '''open_if_statement : IF boolean_expression THEN closed_statement ELSE open_statement'''
    p[0] = IfNode(p[2], p[4], p[6])
    p[0].pos_info = get_pos(p, 0)


def p_closed_if_statement_1(p):
    '''closed_if_statement : IF boolean_expression THEN closed_statement ELSE closed_statement'''
    p[0] = IfNode(p[2], p[4], p[6])
    p[0].pos_info = get_pos(p, 0)


def p_assignment_statement_1(p):
    '''assignment_statement : variable_access ASSIGNMENT expression'''
    p[0] = AssignmentNode(p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_variable_access_1(p):
    '''variable_access : identifier'''
    p[0] = VarAccessNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_variable_access_2(p):
    '''variable_access : indexed_variable'''
    p[0] = p[1]


def p_variable_access_3(p):
    '''variable_access : field_designator'''
    p[0] = p[1]


def p_variable_access_4(p):
    '''variable_access : variable_access UPARROW'''
    p[0] = PointerAccessNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_indexed_variable_1(p):
    '''indexed_variable : variable_access LBRAC index_expression_list RBRAC'''
    p[0] = IndexedVarNode(p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_index_expression_list_1(p):
    '''index_expression_list : index_expression_list comma index_expression'''
    p[0] = ExprListNode(p[3], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_index_expression_list_2(p):
    '''index_expression_list : index_expression'''
    p[0] = ExprListNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_index_expression_1(p):
    '''index_expression : expression'''
    p[0] = p[1]


def p_field_designator_1(p):
    '''field_designator : variable_access DOT identifier'''
    p[0] = FieldAccessNode(p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_procedure_statement_1(p):
    '''procedure_statement : identifier params'''
    p[0] = FunctionCallNode(p[1], p[2])
    p[0].pos_info = get_pos(p, 0)


def p_procedure_statement_2(p):
    '''procedure_statement : identifier'''
    p[0] = FunctionCallNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_params_1(p):
    '''params : LPAREN actual_parameter_list RPAREN'''
    p[0] = p[2]


def p_actual_parameter_list_1(p):
    '''actual_parameter_list : actual_parameter_list comma actual_parameter'''
    p[0] = ArgumentListNode(p[3], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_actual_parameter_list_2(p):
    '''actual_parameter_list : actual_parameter'''
    p[0] = ArgumentListNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_actual_parameter_1(p):
    '''actual_parameter : expression'''
    p[0] = ArgumentNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_actual_parameter_2(p):
    '''actual_parameter : expression COLON expression'''
    p[0] = ArgumentNode(p[1])
    p[0].pos_info = get_pos(p, 0)
    # TODO: parameter formatting


def p_actual_parameter_3(p):
    '''actual_parameter : expression COLON expression COLON expression'''
    p[0] = ArgumentNode(p[1])
    p[0].pos_info = get_pos(p, 0)
    # TODO: parameter formatting


def p_goto_statement_1(p):
    '''goto_statement : GOTO label'''
    p[0] = GotoNode(p[2])
    p[0].pos_info = get_pos(p, 0)


def p_case_statement_1(p):
    '''case_statement : CASE case_index OF case_list_element_list END'''
    p[0] = CaseStatementNode(p[2], p[4])
    p[0].pos_info = get_pos(p, 0)


def p_case_statement_2(p):
    '''
    case_statement : CASE case_index OF case_list_element_list SEMICOLON END
    '''
    p[0] = CaseStatementNode(p[2], p[4])
    p[0].pos_info = get_pos(p, 0)


def p_case_statement_3(p):
    '''case_statement : CASE case_index OF case_list_element_list semicolon otherwisepart statement END'''
    p[0] = CaseStatementNode(p[2], p[4], p[7])
    p[0].pos_info = get_pos(p, 0)


def p_case_statement_4(p):
    '''case_statement : CASE case_index OF case_list_element_list semicolon otherwisepart statement SEMICOLON END'''
    p[0] = CaseStatementNode(p[2], p[4], p[7])
    p[0].pos_info = get_pos(p, 0)


def p_case_index_1(p):
    '''case_index : expression'''
    p[0] = p[1]


def p_case_list_element_list_1(p):
    '''
    case_list_element_list : case_list_element_list semicolon case_list_element
    '''
    p[0] = CaseListElementListNode(p[3], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_case_list_element_list_2(p):
    '''case_list_element_list : case_list_element'''
    p[0] = CaseListElementListNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_case_list_element_1(p):
    '''case_list_element : case_constant_list COLON statement'''
    p[0] = CaseListElementNode(p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_otherwisepart_1(p):
    '''otherwisepart : OTHERWISE'''
    p[0] = p[1].lower()


def p_otherwisepart_2(p):
    '''otherwisepart : OTHERWISE COLON'''
    p[0] = p[1].lower()


def p_control_variable_1(p):
    '''control_variable : identifier'''
    p[0] = p[1]


def p_initial_value_1(p):
    '''initial_value : expression'''
    p[0] = p[1]


def p_direction_1(p):
    '''direction : TO'''
    p[0] = p[1].lower()


def p_direction_2(p):
    '''direction : DOWNTO'''
    p[0] = p[1].lower()


def p_final_value_1(p):
    '''final_value : expression'''
    p[0] = p[1]


def p_record_variable_list_1(p):
    '''record_variable_list : record_variable_list comma variable_access'''
    p[0] = IdentifierListNode(p[3], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_record_variable_list_2(p):
    '''record_variable_list : variable_access'''
    p[0] = IdentifierListNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_boolean_expression_1(p):
    '''boolean_expression : expression'''
    p[0] = p[1]


def p_expression_1(p):
    '''expression : simple_expression'''
    p[0] = p[1]


def p_expression_2(p):
    '''expression : simple_expression relop simple_expression'''
    p[0] = BinaryOpNode(p[2], p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_simple_expression_1(p):
    '''simple_expression : term'''
    p[0] = p[1]


def p_simple_expression_2(p):
    '''simple_expression : simple_expression addop term'''
    p[0] = BinaryOpNode(p[2], p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_term_1(p):
    '''term : factor'''
    p[0] = p[1]


def p_term_2(p):
    '''term : term mulop factor'''
    p[0] = BinaryOpNode(p[2], p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_factor_1(p):
    '''factor : sign factor'''
    p[0] = UnaryOpNode(p[1], p[2])
    p[0].pos_info = get_pos(p, 0)


def p_factor_2(p):
    '''factor : primary'''
    p[0] = p[1]


def p_primary_1(p):
    '''primary : variable_access'''
    p[0] = VarLoadNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_primary_2(p):
    '''primary : unsigned_constant'''
    p[0] = p[1]


def p_primary_3(p):
    '''primary : function_designator'''
    p[0] = p[1]


def p_primary_4(p):
    '''primary : set_constructor'''
    p[0] = p[1]


def p_primary_5(p):
    '''primary : LPAREN expression RPAREN'''
    p[0] = p[2]


def p_primary_6(p):
    '''primary : NOT primary'''
    p[0] = UnaryOpNode(p[1].lower(), p[2])
    p[0].pos_info = get_pos(p, 0)


def p_unsigned_constant_1(p):
    '''unsigned_constant : unsigned_number'''
    p[0] = p[1]


def p_unsigned_constant_2(p):
    '''unsigned_constant : STRING'''
    p[0] = StringNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_unsigned_constant_3(p):
    '''unsigned_constant : NIL'''
    p[0] = NullNode()
    p[0].pos_info = get_pos(p, 0)


def p_unsigned_constant_4(p):
    '''unsigned_constant : CHAR'''
    p[0] = CharNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_unsigned_number_1(p):
    '''unsigned_number : unsigned_integer'''
    p[0] = p[1]


def p_unsigned_number_2(p):
    '''unsigned_number : unsigned_real'''
    p[0] = p[1]


def p_unsigned_integer_1(p):
    '''unsigned_integer : DIGSEQ'''
    p[0] = IntegerNode(int(p[1]))
    p[0].pos_info = get_pos(p, 0)


def p_unsigned_integer_2(p):
    '''unsigned_integer : HEXDIGSEQ'''
    p[0] = IntegerNode(int(p[1][:-1], 16))
    p[0].pos_info = get_pos(p, 0)


def p_unsigned_integer_3(p):
    '''unsigned_integer : OCTDIGSEQ'''
    p[0] = IntegerNode(int(p[1][:-1], 8))
    p[0].pos_info = get_pos(p, 0)


def p_unsigned_integer_4(p):
    '''unsigned_integer : BINDIGSEQ'''
    p[0] = IntegerNode(int(p[1][:-1], 2))
    p[0].pos_info = get_pos(p, 0)


def p_unsigned_real_1(p):
    '''unsigned_real : REALNUMBER'''
    p[0] = RealNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_function_designator_1(p):
    '''function_designator : identifier params'''
    p[0] = FunctionCallNode(p[1], p[2])
    p[0].pos_info = get_pos(p, 0)


def p_set_constructor_1(p):
    '''set_constructor : LBRAC member_designator_list RBRAC'''
    p[0] = SetNode(p[2])
    p[0].pos_info = get_pos(p, 0)


def p_set_constructor_2(p):
    '''set_constructor : LBRAC RBRAC'''
    p[0] = SetEmptyNode()
    p[0].pos_info = get_pos(p, 0)


def p_member_designator_list_1(p):
    '''
    member_designator_list : member_designator_list comma member_designator
    '''
    p[0] = SetMemberListNode(p[3], p[1])
    p[0].pos_info = get_pos(p, 0)


def p_member_designator_list_2(p):
    '''member_designator_list : member_designator'''
    p[0] = SetMemberListNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_member_designator_1(p):
    '''member_designator : member_designator DOTDOT expression'''
    p[0] = SetMemberRangeNode(p[1], p[3])
    p[0].pos_info = get_pos(p, 0)


def p_member_designator_2(p):
    '''member_designator : expression'''
    p[0] = p[1]


def p_addop_1(p):
    '''addop : PLUS'''
    p[0] = OpNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_addop_2(p):
    '''addop : MINUS'''
    p[0] = OpNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_addop_3(p):
    '''addop : OR'''
    p[0] = OpNode(p[1].lower())
    p[0].pos_info = get_pos(p, 0)


def p_mulop_1(p):
    '''mulop : STAR'''
    p[0] = OpNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_mulop_2(p):
    '''mulop : SLASH'''
    p[0] = OpNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_mulop_3(p):
    '''mulop : DIV'''
    p[0] = OpNode(p[1].lower())
    p[0].pos_info = get_pos(p, 0)


def p_mulop_4(p):
    '''mulop : MOD'''
    p[0] = OpNode(p[1].lower())
    p[0].pos_info = get_pos(p, 0)


def p_mulop_5(p):
    '''mulop : AND'''
    p[0] = OpNode(p[1].lower())
    p[0].pos_info = get_pos(p, 0)


def p_relop_1(p):
    '''relop : EQUAL'''
    p[0] = OpNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_relop_2(p):
    '''relop : NOTEQUAL'''
    p[0] = OpNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_relop_3(p):
    '''relop : LT'''
    p[0] = OpNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_relop_4(p):
    '''relop : GT'''
    p[0] = OpNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_relop_5(p):
    '''relop : LE'''
    p[0] = OpNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_relop_6(p):
    '''relop : GE'''
    p[0] = OpNode(p[1])
    p[0].pos_info = get_pos(p, 0)


def p_relop_7(p):
    '''relop : IN'''
    p[0] = OpNode(p[1].lower())
    p[0].pos_info = get_pos(p, 0)


def p_identifier_1(p):
    '''identifier : IDENTIFIER'''
    p[0] = IdentifierNode((p[1]).lower())
    p[0].pos_info = get_pos(p, 0)


def p_semicolon_1(p):
    '''semicolon : SEMICOLON'''
    p[0] = p[1]


def p_comma_1(p):
    '''comma : COMMA'''
    p[0] = p[1]


def p_error(p):
    if p:
        log.e("grammar", "invalid token '%s' at (%s, %d)" %
                         (p.value, p.lineno, p.lexpos))
    else:
        log.e("grammar", "unknown error")


def p_empty_1(p):
    '''empty : '''
    pass


def parser(debug=False):
    if debug:
        logger = yacc.PlyLogger(sys.stderr)
    else:
        logger = yacc.NullLogger()

    tab = "llvm_p86._p86_parsetab"
    mod = sys.modules[__name__]
    return yacc.yacc(debuglog=logger,
                     errorlog=logger,
                     optimize=1,
                     tabmodule=tab,
                     outputdir=os.path.dirname(__file__),
                     module=mod)


def get_pos(p, num):
    line = p.lineno(num)
    span = p.lexspan(num)

    class PosInfo(object):
        def __init__(self, **kwargs):
            self.__dict__ = kwargs

        def __str__(self):
            return str(self.path[-1]) + ':' + str(self.lineno)

    return PosInfo(path=line[0],
                   lineno=line[1],
                   lexpos=span[0],
                   lexendpos=span[1])


def get_len(p, num):
    span = p.lexspan(num)
    length = span[1] - span[0]
    if length == 0 and p[num] is not None:
        length = len(p[num])

    return length
