program CaseTest;

var
   age : integer;
begin
   age := 2;
   
   case age of
     0,1       : halt(1);
     2	       : writeln('OK');
     otherwise : halt(1)
   end; { case }

   age := 5;
   
end.