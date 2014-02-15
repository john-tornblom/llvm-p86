program IfTest;
var
   i : integer;
   j : integer;
begin
   i := 0;
   j := 2;
   
   if i = 0 then
      writeln('OK')
   else
      halt(1);
   
   if i <> 0 then
   begin
      halt(1);
   end
   else
      if i <> 0 then
      begin
	 halt(1);
      end
      else
	 if i <> 0 then
	 begin
	    halt(1);
	 end
	 else
	    writeln('OK');
   
end.

