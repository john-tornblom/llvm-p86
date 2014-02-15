[inherit('lib1', 'lib2', 'lib3')] Program VaxTest(input, output);


{ %include 'libc.pas' }

Const
   STRING_LEN = 10;

Var
   status : (OK, NOK);
   b	  : boolean;
   i	  : integer;
   r	  : real;
   s	  : [external] varying [STRING_LEN] of char;


procedure debug(prefix : varying [STRING_LEN] of char);
begin
   WriteLn(prefix);
end; { debug }


begin
   WriteLn('HELLO WORLD');
end.

