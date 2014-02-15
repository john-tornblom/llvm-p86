Procedure Assert(value, expected: Boolean);
Begin
   If value = expected Then
      Writeln('OK')
   Else
      Halt(1);
End; { Assert }

Procedure AssertInt(value, expected: Integer);
Begin
   If value = expected Then
      Writeln('OK')
   Else
      Halt(1);
End; { AssertInt }
