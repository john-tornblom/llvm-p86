program ProcedureTest;
var
   r,tmp : real;

procedure fsum(var num: real; num2 : real);
   procedure fsum_inner;
   begin
      if num = 5 then
	 writeln('OK')
      else
	 halt(1);

      num := 0;
   end;
begin
   fsum_inner;
   r := num + num2;
end; { fsum }

begin
   tmp := 5;
   fsum(tmp, 2);

   if tmp = 0 then
      writeln('OK')
   else
      halt(1);
end.
