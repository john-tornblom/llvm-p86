program testLabel;

label
   1,2,3,4,5;
   
const
   OK  = 'OK';

var
   i : integer;
   
begin
   goto 1;
   halt(1);
   1: writeln(OK);
   
   goto 2;
   halt(1);
   2: writeln(OK);


   i := 0;
   3: writeln(OK);
   i := i+1;
   if i < 2 then
   begin
      goto 3;
   end;

   case i of
     0,1   : writeln('ERROR');
     2,3,4 : goto 3;
     5..12 : goto 4;
     13..19: writeln('ERROR');
     20..25: writeln('ERROR');

   end; { case }

   4: writeln(OK);

   for i := 0 to 5 do
   begin
      5: writeln('OK');
   end;

   if i = 6 then
      goto 5;
   
   if i <> 7 then
      writeln('ERROR');
end.