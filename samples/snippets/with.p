Program WithTest;

Type
   T_DATE = Record
	       day   : Integer;
	       month : Integer;
	       year  : Integer;
	    end;     
	     
Var
   date	: T_DATE;

Procedure Copy(Var ref : Integer; value : Integer);
Begin
   ref := value;
End; { Copy }


Procedure Assert(value, expected : Integer);
Begin
   If value = expected Then
      Writeln('OK')
   Else
      Halt(1);
End; { Assert }

Begin
   date.day := 3;
   date.month := 1;
   date.year := 1984;
   
   Assert(date.day, 3);
   Assert(date.month, 1);
   Assert(date.year, 1984);

   With date do
   Begin
      Assert(day, 3);
      Assert(month, 1);
      Assert(year, 1984);

      day := 1;
      month := 2;
      year := 3;

      Assert(day, 1);
      Assert(month, 2);
      Assert(year, 3);

      Copy(day, 0);
      Copy(month, 0);
      Copy(year, 0);
      
      Assert(day, 0);
      Assert(month, 0);
      Assert(year, 0);
   End;

   Assert(date.day, 0);
   Assert(date.month, 0);
   Assert(date.year, 0);
   
End.
