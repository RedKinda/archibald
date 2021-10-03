use std::str;


pub(crate) fn preprocess(program: &str) -> String{
    let mut s: String = program.to_string();

    if s.starts_with("~") {
        if let Some(index) = s.find(" ") {
            s = s[index..].parse().unwrap();
        }
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

        s.insert_str(start_at, "\nvoid main() ");
    }

    if !s.contains("return") && s.contains("int main") {
        s = s.replace("int main", "void main");
    }

    if s.contains("cout") {
        if !s.contains("iostream") {
            s.insert_str(0, "#include <iostream>\n");
        }
    }

    s
}