program CaseTest;

type
   T_UINT4	= 0..15;
   T_NUMBER	= (ONE, TWO, THREE, FOUR, FIVE);
   T_MID_NUMBER	= TWO..FOUR;
var
   age : integer;
   i   : integer;
   ch  : char;
   u4  : T_UINT4;
   mid : T_MID_NUMBER;
begin
   age := 2;
   
   case age of
     0,1       : halt(1);
     2,3,4     : writeln('OK');
     5..12: halt(1);
     13..19: halt(1);
     20..25: halt(1);
     otherwise : halt(1)
   end; { case }

   age := 4;
   
   case age of
     0,1       : halt(1);
     2,3,4     : writeln('OK');
     5..12: halt(1);
     13..19: halt(1);
     20..25: halt(1);
     otherwise : halt(1)
   end; { case }

   age := 25;
   
   case age of
     0,1       : halt(1);
     2,3,4     : halt(1);
     5..12: halt(1);
     13..19: halt(1);
     20..25: writeln('OK');
     otherwise : halt(1)
   end; { case }

   age := 20;
   
   case age of
     0,1       : halt(1);
     2,3,4     : halt(1);
     5..12: halt(1);
     13..19: halt(1);
     20..25: writeln('OK');
     otherwise : halt(1)
   end; { case }

   age := 26;
   
   case age of
     0,1       : halt(1);
     2,3,4     : halt(1);
     5..12: halt(1);
     13..19: halt(1);
     20..25: halt(1);
     otherwise : writeln('OK')
   end; { case }


   age := -5;
   
   case age of
     -5,0,1 : writeln('OK');
     2,3,4  : halt(1);
     5..12: halt(1);
     13..19: halt(1);
     20..25: halt(1);
     otherwise : halt(1)
   end; { case }

   
   ch := 'a';

   case ch of
     'a'       : writeln('OK');
     'b'       : halt(1);
     'c', 'd'  : halt(1);
     'e'..'z'  : halt(1);
     otherwise : halt(1)
   end; { case }

   ch := 'd';

   case ch of
     'a'       : halt(1);
     'b'       : halt(1);
     'c', 'd'  : writeln('OK');
     'e'..'z'  : halt(1);
     otherwise : halt(1)
   end; { case }

   ch := 'p';

   case ch of
     'a'       : halt(1);
     'b'       : halt(1);
     'c', 'd'  : halt(1);
     'e'..'z'  : writeln('OK');
     otherwise : halt(1)
   end; { case }

   ch := ' ';

   case ch of
     'a'       : halt(1);
     'b'       : halt(1);
     'c', 'd'  : halt(1);
     'e'..'z'  : halt(1);
     otherwise : writeln('OK')
   end; { case }


   age := 0;

   for i := 1 to 10 do
      case i of
	1     : age := age + 1;
	2     : age := age + 1;
	3     : age := age + 1;
	4     : age := age + 1;
	5     : age := age + 1;
	6     : age := age + 1;
	7     : age := age + 1;
	8     : age := age + 1;
	9, 10 : age := age + 1;
      end; { case }

   if age = 10 then
      writeln('OK')
   else
      halt(1);
   
   age := 0;

   for i := 1 to 10 do
      case i of
	1     : age := age + 1;
	2     : age := age + 1;
	3     : age := age + 1;
	4     : age := age + 1;
	5     : age := age + 1;
	6     : age := age + 1;
	7     : age := age + 1;
	8     : age := age + 1;
	9, 10 : age := age + 1
      end; { case }

   if age = 10 then
      writeln('OK')
   else
      halt(1);

   age := 4;
   i := 3;

   case age of
     4 : begin
	    if i = 3 then
	       writeln('OK')
	    else
	       halt(1);
	 end;
     otherwise : halt(1)
   end; { case }

   u4 := 0;

   case u4 of
     0 : writeln('OK');
     1,2,3,4  : halt(1);
     otherwise : halt(1)
   end; { case }

   mid := THREE;

   case mid of
     TWO   : halt(1);
     THREE : writeln('OK');
     FOUR  : halt(1);
   end; { case }
end.
   