program ArrayTest;

const
   OK  = 'OK';
   
var
   arr		   : array[0..10] of integer;
   str		   : array[1..10] of char;
   i		   : integer;
   j		   : integer;
   table	   : array [0..10] of record
	      name : char;
	      kind : integer;
           end;	   
begin  
   
   for i := 0 to 9 do
   begin
      arr[i] := 1;
   end;
   
   j := 0;
   
   for i := 0 to 9 do
   begin
      j := j + arr[i];
   end;
   
   if j = 10 then
      writeln(OK)
   else
      halt(1);

   table[0].name := 'a';
   table[0].kind := 1;

   table[1] := table[0];

   if table[1].name = 'a' then
      writeln(OK)
   else
      halt(1);

   if table[1].kind = 1 then
      writeln(OK)
   else
      halt(1);

   str := OK;
   writeln(str[1], str[2]);
end.

