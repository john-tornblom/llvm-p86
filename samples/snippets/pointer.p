program PointerTest;

const
   OK  = "OK";

type
   T_DATE = record
	       day   : integer;
	       month : integer;
	       year  : integer;
	    end;
var
   i	  : integer;
   arr	  : array[0..10] of integer;
   date	  : T_DATE;
   p_list : array [0..10] of ^integer;
   
procedure init(var ref : integer; val : integer);
begin
   ref := val;
end; { init }

begin
   i := 1;
   
   init(i, i + i);
   if i = 2 then
      writeln(OK)
   else
      halt(1);

   for i := 0 to 9 do
   begin
      arr[i] := 0;
   end;
   
   for i := 0 to 9 do
   begin
      arr[i] := 0;
      init(arr[i], i);
      
      if arr[i] = i then
	 writeln(OK)
      else
	 halt(1);
   end;


   init(date.year, 1984);
   init(date.month, 1);
   init(date.day, 3);

   if date.year = 1984 then
      writeln(OK)
   else
      halt(1);

   if date.month = 1 then
      writeln(OK)
   else
      halt(1);

   if date.day = 3 then
      writeln(OK)
   else
      halt(1);

   p_list[0] := nil;
end.