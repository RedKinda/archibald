use std::str;


pub(crate) fn preprocess(program: &str) -> String{
    let mut s: String = program.to_string();

    if s.starts_with("~") {
        let index_to_remove = {
            let mut i= 6;
            if let Some(index) = s.find(" ") {
                i = index;
            }
            if let Some(index) = s.find("\n") {
                if index < i {
                    i = index
                }
            }
            i
        };
        s = s[index_to_remove..].parse().unwrap();
    }

    if s.contains("```") {
        let indices: Vec<_> = s.match_indices("```").collect();

        if indices.len() >= 2 {
            s = s[indices[0].0 + 3..indices[1].0].parse().unwrap();
        }

        if s.starts_with("cpp") {
            s = s[3..].parse().unwrap();
        }
    }

    let mut includes: Vec<String> = vec!();
    for line in s.lines() {
        let (first_char, index) = {
            let mut ans = ' ';
            let mut index = 0;
            for c in line.chars() {
                if c != ' ' {
                    ans = c;
                    break;
                }
                index += 1;
            }
            (ans, index)
        };
        if first_char.eq(&'#') {
            includes.push(line[index..].to_string());
        }
    }

    for inc in &includes {
        s = s.replace(inc, "");
    }

    if !s.contains("{") {
        s.insert_str(0, "{\n");
        s = s + "\n}";
    }

    if !s.contains("main") {
        let start_at = {
            if let Some(first_bracket) = s.find("{") {
                first_bracket
            } else {
                0
            }
        };

        s.insert_str(start_at, "\nint main() ");
    }

    if !s.contains("return") {
        let indices: Vec<_> = s.match_indices("}").collect();
        let last_bracket = indices.last().expect("} must be in code at this point").0;
        s.insert_str(last_bracket, "\nreturn 0;\n")
    }

    for inc in includes {
        s.insert(0, '\n');
        s.insert_str(0, &*inc)
    }

    if s.contains("cout") {
        if !s.contains("iostream") {
            s.insert_str(0, "#include <iostream>\n");
        }
    }

    s
}